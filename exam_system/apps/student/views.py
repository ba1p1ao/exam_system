from rest_framework.views import APIView
from django.db.models import Max, Min, Avg, Count, Case, When, FloatField
from django.utils import timezone
from apps.user.models import User
from apps.exam.models import ExamRecord, Exam
from apps.classes.models import Class, UserClass
from utils.ResponseMessage import check_auth, check_permission, MyResponse
from utils.CacheConfig import (
    CACHE_KEY_CLASS_TREND,
    CACHE_TIMEOUT_CLASS_TREND,
    CACHE_TIMEOUT_STUDENT_CLASS,
    CACHE_KEY_STUDENT_CLASS,
    generate_cache_key, get_cache_timeout,
)
from utils.CacheTools import cache_delete_pattern
from django.core.cache import cache
from datetime import timedelta


class ScoreTrendView(APIView):
    @check_auth
    def get(self, request):
        payload = request.user
        if payload.get("role") != "student":
            return MyResponse.success()
        user_id = payload.get("id")

        days = int(request.GET.get("days"))

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_CLASS_TREND, user_id=user_id, days=days)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        timeago = timezone.now() - timedelta(days=days)
        exam_records = ExamRecord.objects.filter(user_id=user_id, status="graded",
                                                 exam__end_time__gte=timeago).select_related('exam')
        if not exam_records:
            return MyResponse.failed(message="暂无考试成绩记录")
        try:
            stats = exam_records.aggregate(
                total_exams=Count("id"),
                average_score=Avg("score"),
                highest_score=Max("score"),
                lowest_score=Min("score"),
                pass_rate=Avg(
                    Case(
                        When(is_passed=1, then=1.0),
                        When(is_passed=0, then=0.0),
                        default=None,
                        output_field=FloatField()
                    )
                )
            )
        except Exception as e:
            return MyResponse.failed(message=f"获取成绩记录发生错误，{e}")

        trend_list = []
        for exam_record in exam_records:
            trend_list.append({
                "date": exam_record.submit_time.strftime("%Y-%m-%d %H:%M:%S") if exam_record.submit_time else None,
                "exam_title": exam_record.exam.title,
                "score": exam_record.score
            })

        response_data = {
            "total_exams": stats.get("total_exams"),
            "average_score": stats.get("average_score"),
            "highest_score": stats.get("highest_score"),
            "lowest_score": stats.get("lowest_score"),
            "pass_rate": stats.get("pass_rate"),
            "trend": trend_list
        }

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_CLASS_TREND))
        return MyResponse.success(data=response_data)


class StudentClassView(APIView):
    @check_auth
    def get(self, request):
        payload = request.user
        user_id = payload.get("id")

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_STUDENT_CLASS, user_id=user_id)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 获取学生所在的班级
        class_info = Class.objects.filter(userclass__user_id=user_id).first()
        if not class_info:
            return MyResponse.failed(message="您还未加入班级")

        # 获取当前班级所有学生
        students = UserClass.objects.filter(class_info_id=class_info.id, user__role="student")
        student_count = students.count()

        # 获取当前学生的加入时间
        try:
            current_student = students.get(user_id=user_id)
            join_time = current_student.join_time.strftime("%Y-%m-%d %H:%M:%S")
        except UserClass.DoesNotExist:
            join_time = None

        # 获取班主任姓名
        head_teacher_name = class_info.head_teacher.username if class_info.head_teacher else None

        # 计算班级排名（基于平均分）
        # 获取班级所有学生的平均分
        from django.db.models import Avg
        student_scores = ExamRecord.objects.filter(
            user_id__in=students.values_list('user_id', flat=True),
            status="graded"
        ).values('user_id').annotate(
            avg_score=Avg('score'),
            exam_count=Count('id')
        ).order_by('-avg_score')

        # 计算当前学生的排名
        my_rank = None
        for idx, score_data in enumerate(student_scores, 1):
            if score_data['user_id'] == user_id:
                my_rank = idx
                break

        response_data = {
            "id": class_info.id,
            "name": class_info.name,
            "grade": class_info.grade,
            "head_teacher_name": head_teacher_name,
            "student_count": student_count,
            "join_time": join_time,
            "my_rank": my_rank,
        }

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_STUDENT_CLASS))
        return MyResponse.success(data=response_data)


class StudentScoreComparisonView(APIView):
    @check_auth
    def get(self, request):
        payload = request.user

        user_id = payload.get("id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户信息不存在")
        # 获取用户参加过的考试记录（已阅卷），按考试分组取最高分
        exam_records = ExamRecord.objects.filter(user_id=user_id, status="graded").values("exam_id").annotate(
            max_score=Max("score")
        ).order_by("exam_id")

        # 初始化相应数据
        response_data = {
            "my_scores": [],
            "class_average": [],
            "exam_titles": []
        }
        if not exam_records.exists():
            return MyResponse.success(data=response_data)

        # 获取考试ID列表
        exam_ids = [er["exam_id"] for er in exam_records]
        # 获取用户所在班级的所有学生
        class_student_ids = User.objects.filter(class_id=user.class_id, role="student").values_list("id", flat=True)

        # 如果班级只有自己
        if len(class_student_ids) == 1:
            return MyResponse.success(data={
                "my_scores": [er["max_score"] for er in exam_records],
                "class_average": [er["max_score"] for er in exam_records],  # 班级平均就是自己的成绩
                "exam_titles": []
            })

        # 获取班级所有学生在这些考试中的记录
        cur_class_student_exam_record = ExamRecord.objects.filter(
            exam_id__in=exam_ids, user_id__in=class_student_ids, status="graded"
        )

        # 计算每个考试的班级平均分
        class_avg_scores = cur_class_student_exam_record.values("exam_id", "exam__title").annotate(
            class_average=Avg("score")
        ).order_by("exam_id")

        # 构建考试ID到平均分的映射
        exam_avg_map = {cas["exam_id"]: cas["class_average"] for cas in class_avg_scores}
        exam_title_map = {cas["exam_id"]: cas["exam__title"] for cas in class_avg_scores}

        # 构建响应数据
        my_scores = []
        class_average = []
        exam_titles = []
        for er in exam_records:
            exam_id = er["exam_id"]
            my_scores.append(er["max_score"])
            class_average.append(exam_avg_map.get(exam_id, 0))
            exam_titles.append(exam_title_map.get(exam_id, f"考试{exam_id}"))

        response_data = {
            "my_scores": my_scores,
            "class_average": class_average,
            "exam_titles": exam_titles
        }
        return MyResponse.success(data=response_data)
