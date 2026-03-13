import logging
from django.db.models import Count, F, Q, Avg, Max, Min, Case, When, FloatField
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from rest_framework.views import APIView
from apps.classes.serializers import ClassListSerializer
from apps.classes.models import Class, UserClass
from apps.exam.models import ExamRecord, Exam, ExamClass
from apps.user.models import User
from utils.ResponseMessage import check_auth, check_permission, MyResponse
from utils.CacheConfig import (
    CACHE_KEY_CLASS_LIST,
    CACHE_TIMEOUT_CLASS_LIST,
    CACHE_KEY_CLASS_STATISTICS,
    CACHE_TIMEOUT_CLASS_STATISTICS,
    CACHE_KEY_CLASS_RANKING,
    CACHE_TIMEOUT_CLASS_RANKING,
    CACHE_KEY_CLASS_TREND,
    CACHE_TIMEOUT_CLASS_TREND,
    CACHE_KEY_CLASS_MEMBERS,
    CACHE_TIMEOUT_CLASS_MEMBERS,
    CACHE_TIMEOUT_EMPTY_RESULT,
    CACHE_KEY_STUDENT_CLASS,
    generate_cache_key,
    generate_filter_key,
    get_cache_timeout, CACHE_KEY_USER_STATISTICS, CACHE_KEY_SYSTEM_STATISTICS,

)
from utils.CacheTools import cache_delete_pattern
from django.core.cache import cache

logger = logging.getLogger('apps')


class ClassOptionView(APIView):
    @check_permission
    def get(self, request):
        payload = request.user

        classes = Class.objects.all()
        if not classes:
            return MyResponse.failed("没有班级信息，请添加班级")
        response_data = []
        for c in classes:
            response_data.append({
                "id": c.id,
                "name": c.name,
                "grade": c.grade
            })

        return MyResponse.success(data=response_data)


class ClassListView(APIView):
    @check_permission
    def get(self, request):
        payload = request.user
        request_data = request.GET

        filter_body = {}
        page = int(request_data.get("page", 1))
        page_size = int(request_data.get("size", 10))
        for k, v in request_data.items():
            if k in ["page", "size"]:
                continue
            elif k == "name" and v:
                filter_body["name__icontains"] = v
            elif k in ["grade", "status"] and v:
                filter_body[k] = v

        offset = (page - 1) * page_size

        # 构建缓存键
        cache_filters = generate_filter_key(filter_body)
        cache_key = generate_cache_key(
            CACHE_KEY_CLASS_LIST, filter=cache_filters, page=page, size=page_size
        )
        # 获取缓存数据
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        classes = Class.objects.filter(**filter_body).select_related('head_teacher').annotate(
            student_count=Count("userclass__user")
        )
        if not classes:
            return MyResponse.failed(message="当前没有班级信息")

        response_data = {
            "list": [],
            "total": classes.count(),
            "page": page,
            "size": page_size
        }
        page_list = classes[offset:offset + page_size]
        try:
            for c in page_list:
                class_data = {}
                class_data["id"] = c.id
                class_data["name"] = c.name
                class_data["grade"] = c.grade
                class_data["head_teacher_id"] = c.head_teacher.id if c.head_teacher else None
                class_data["head_teacher_name"] = c.head_teacher.username if c.head_teacher else None
                class_data["student_count"] = c.student_count
                class_data["status"] = c.status
                class_data["create_time"] = c.create_time.strftime("%Y-%m-%d %H:%M:%S")
                response_data["list"].append(class_data)
            # 设置缓存
            if not page_list:
                cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_EMPTY_RESULT))
            else:
                cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_CLASS_LIST))
            return MyResponse.success(data=response_data)
        except Exception as e:
            return MyResponse.failed(message=f"获取班级信息出错，{e}")


class ClassCreateView(APIView):
    @check_permission
    def post(self, request):
        payload = request.user

        request_data = request.data
        if not request_data.get("head_teacher_id"):
            return MyResponse.failed(message="请选择教师信息")

        try:
            user_teacher = User.objects.get(id=request_data["head_teacher_id"])
        except User.DoesNotExist:
            return MyResponse.failed(message="教师信息不存在")

        if user_teacher.role != "teacher":
            return MyResponse.failed(message="请选择教师角色作为班主任")

        class_obj = Class.objects.filter(name=request_data["name"])
        if class_obj:
            return MyResponse.failed(message="班级名称已存在")

        try:
            with transaction.atomic():
                # 添加班级信息
                create_class = Class.objects.create(**request_data)

                # 将教师信息，添加到该班级里面
                create_user_class = UserClass.objects.create(user=user_teacher, class_info=create_class)
                # 修改用户表中的class_id
                User.objects.filter(id=user_teacher.id).update(class_id=create_class.id)

            logger.info(f"用户 {payload.get('username')} 创建班级成功: {create_class.name}")
            # 清除班级列表缓存
            cache_delete_pattern("class:list:*")
            return MyResponse.success(message="班级添加成功")
        except Exception as e:
            logger.error(f"用户 {payload.get('username')} 创建班级失败: {e}")
            return MyResponse.failed(message=f"添加班级错误，{e}")


class ClassView(APIView):
    @check_permission
    def put(self, request, class_id):
        payload = request.user
        request_data = request.data
        if not request_data.get("head_teacher_id"):
            return MyResponse.failed(message="请选择教师信息")

        # 更新班级信息
        update_class = Class.objects.filter(id=class_id).update(**request_data)
        if not update_class:
            return MyResponse.failed(message="班级信息不存在")

        logger.info(f"用户 {payload.get('username')} 更新班级成功，班级ID: {class_id}")
        # 清除班级相关缓存
        cache_delete_pattern("class:list:*")
        cache_delete_pattern("class:statistics:*")
        cache_delete_pattern("class:members:*")
        cache_delete_pattern("class:ranking:*")
        cache_delete_pattern("class:trend:*")
        # 清除教师班级缓存
        cache_delete_pattern("teacher:class:*")
        # 清除学生班级信息缓存
        cache_delete_pattern("user:class:*")
        # 清除统计缓存
        cache.delete(CACHE_KEY_USER_STATISTICS)
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

        return MyResponse.success(message="修改成功")

    @check_permission
    def delete(self, request, class_id):
        payload = request.user
        try:
            # 检查班级是否存在
            class_obj = Class.objects.get(id=class_id)
            # 删除班级，由于 UserClass 的 on_delete=CASCADE，会自动删除关联的学生班级记录
            class_obj.delete()

            logger.info(f"用户 {payload.get('username')} 删除班级成功: {class_obj.name}")
            # 清除班级相关缓存
            cache_delete_pattern("class:list:*")
            cache_delete_pattern("class:statistics:*")
            cache_delete_pattern("class:members:*")
            cache_delete_pattern("class:ranking:*")
            cache_delete_pattern("class:trend:*")
            # 清除教师班级缓存
            cache_delete_pattern("teacher:class:*")
            # 清除学生班级信息缓存
            cache_delete_pattern("user:class:*")
            # 清除统计缓存
            cache.delete(CACHE_KEY_USER_STATISTICS)
            cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
            return MyResponse.success(message="删除成功")
        except Class.DoesNotExist:
            return MyResponse.failed(message="班级信息不存在")
        except Exception as e:
            logger.error(f"用户 {payload.get('username')} 删除班级失败: {str(e)}")
            return MyResponse.failed(message=f"删除失败: {str(e)}")


class ClassStatusView(APIView):
    @check_permission
    def put(self, request, class_id):
        payload = request.user

        # 获取班级信息
        try:
            class_obj = Class.objects.get(id=class_id)
            new_status = 0 if class_obj.status == 1 else 1
            update_class = Class.objects.filter(id=class_id).update(status=new_status)
            if update_class == 0:
                return MyResponse.failed(message="班级信息不存在")

            # 清除班级相关缓存
            cache_delete_pattern("class:list:*")
            cache_delete_pattern("class:statistics:*")
            cache_delete_pattern("class:members:*")
            cache_delete_pattern("class:ranking:*")
            cache_delete_pattern("class:trend:*")
            # 清除教师班级缓存
            cache_delete_pattern("teacher:class:*")
            # 清除学生班级信息缓存
            cache_delete_pattern("user:class:*")
            # 清除统计缓存
            cache.delete(CACHE_KEY_USER_STATISTICS)
            cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
            return MyResponse.success(message="修改成功")
        except Class.DoesNotExist:
            return MyResponse.failed(message="班级信息不存在")


class ClassStatisticsView(APIView):
    @check_permission
    def get(self, request, class_id):
        payload = request.user

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_CLASS_STATISTICS, class_id=class_id)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return MyResponse.failed(message="班级信息不存在")

        response_data = {
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "student_count": 0,
            "exam_count": 0,
            "average_score": 0.00,
            "highest_score": 0.00,
            "lowest_score": 0.00,
            "pass_rate": 0.00,
            "excellent_rate": 0.00,
            "score_distribution": {
                "0-59": 0,
                "60-69": 0,
                "70-79": 0,
                "80-89": 0,
                "90-100": 0
            }
        }

        student_class_qs = UserClass.objects.filter(class_info=class_id, user__role="student").select_related("user")
        response_data["student_count"] = student_class_qs.count()

        if response_data["student_count"] == 0:
            return MyResponse.success(data=response_data)

        student_ids = [s.user_id for s in student_class_qs]

        graded_records = ExamRecord.objects.filter(user_id__in=student_ids, status="graded")
        response_data["exam_count"] = graded_records.count()

        if response_data["exam_count"] == 0:
            return MyResponse.success(data=response_data)

        class_exam_score = graded_records.aggregate(
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
            ),
            excellent_rate=Avg(
                Case(
                    When(score__gte=80, then=1.0),
                    When(score__lt=80, then=0.0),
                    default=None,
                    output_field=FloatField()
                )
            )
        )

        response_data["average_score"] = round(class_exam_score["average_score"] or 0, 2)
        response_data["highest_score"] = round(class_exam_score["highest_score"] or 0, 2)
        response_data["lowest_score"] = round(class_exam_score["lowest_score"] or 0, 2)
        response_data["pass_rate"] = round(class_exam_score["pass_rate"] or 0, 2)
        response_data["excellent_rate"] = round(class_exam_score["excellent_rate"] or 0, 2)

        student_max_scores = graded_records.values("user_id").annotate(max_score=Max("score"))
        for er in student_max_scores:
            max_score = er["max_score"]
            if max_score >= 90:
                response_data["score_distribution"]["90-100"] += 1
            elif max_score >= 80:
                response_data["score_distribution"]["80-89"] += 1
            elif max_score >= 70:
                response_data["score_distribution"]["70-79"] += 1
            elif max_score >= 60:
                response_data["score_distribution"]["60-69"] += 1
            else:
                response_data["score_distribution"]["0-59"] += 1

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_CLASS_STATISTICS))
        return MyResponse.success(data=response_data)


class ClassMembersView(APIView):
    @check_permission
    def get(self, request, class_id):
        payload = request.user

        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("size", 10))
        offset = (page - 1) * page_size

        role = request.GET.get("role", "")

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_CLASS_MEMBERS, class_id=class_id, role=role, page=page, size=page_size)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return MyResponse.failed(message="班级信息不存在")

        user_class_qs = UserClass.objects.filter(class_info=class_id)

        if role:
            user_class_qs = user_class_qs.filter(user__role=role)

        total = user_class_qs.count()

        response_data = {
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "list": [],
            "total": total,
            "page": page,
            "size": page_size,
        }

        if total == 0:
            return MyResponse.success(data=response_data)

        student_list = user_class_qs.select_related('user').order_by("-user__role", "join_time")[offset:offset + page_size]

        for student in student_list:
            data = {
                "id": student.user.id,
                "username": student.user.username,
                "nickname": student.user.nickname,
                "role": student.user.role,
                "avatar": student.user.avatar,
                "status": student.user.status,
                "join_time": student.join_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            response_data["list"].append(data)

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_CLASS_MEMBERS))
        return MyResponse.success(data=response_data)


class ClassMembersAddView(APIView):
    @check_permission
    def post(self, request, class_id):
        payload = request.user
        request_data = request.data

        user_ids = request_data.get("user_ids")

        if not user_ids or not isinstance(user_ids, list):
            return MyResponse.failed(message="请提供有效的用户ID列表")

        if len(user_ids) == 0:
            return MyResponse.failed(message="用户ID列表不能为空")

        users = User.objects.filter(id__in=user_ids)
        if not users:
            return MyResponse.failed(message="用户信息不存在")

        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return MyResponse.failed(message="当前班级不存在")

        existing_user_ids = set(
            UserClass.objects.filter(
                class_info=class_obj,
                user_id__in=user_ids
            ).values_list('user_id', flat=True)
        )

        users_to_add = [user for user in users if user.id not in existing_user_ids]

        if not users_to_add:
            return MyResponse.success(data={
                "success_count": 0,
                "failed_count": len(user_ids),
                "failed_list": [{"user_id": uid, "reason": "用户已在班级中"} for uid in user_ids]
            })

        with transaction.atomic():
            user_class_objects = [
                UserClass(user=user, class_info=class_obj)
                for user in users_to_add
            ]

            created_objects = UserClass.objects.bulk_create(user_class_objects)

            # 修改用户表的班级id
            User.objects.filter(id__in=[user.id for user in users_to_add]).update(class_id=class_id)

        failed_ids = set(user_ids) - {uc.user_id for uc in created_objects}

        response_data = {
            "success_count": len(created_objects),
            "failed_count": len(failed_ids),
            "failed_list": [{"user_id": uid, "reason": "用户已在班级中"} for uid in failed_ids]
        }

        logger.info(f"用户 {payload.get('username')} 添加班级成员成功，班级: {class_obj.name}，成功: {len(created_objects)}，失败: {len(failed_ids)}")
        # 清除班级相关缓存
        cache_delete_pattern("class:list:*")
        cache_delete_pattern("class:statistics:*")
        cache_delete_pattern("class:members:*")
        cache_delete_pattern("class:ranking:*")
        cache_delete_pattern("class:trend:*")
        # 清除教师班级缓存
        cache_delete_pattern("teacher:class:*")
        # 清除学生班级信息缓存
        cache_delete_pattern("user:class:*")
        # 清除统计缓存
        cache.delete(CACHE_KEY_USER_STATISTICS)
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

        return MyResponse.success(data=response_data)


class ClassMembersRemoveView(APIView):
    @check_permission
    def delete(self, request, class_id):
        payload = request.user
        request_data = request.data
        user_ids = request_data.get("user_ids")

        if not user_ids or not isinstance(user_ids, list):
            return MyResponse.failed(message="请提供有效的用户ID列表")

        if len(user_ids) == 0:
            return MyResponse.failed(message="用户ID列表不能为空")

        if payload.get("id") in user_ids:
            return MyResponse.failed(message="不能删除自己的信息")

        users = User.objects.filter(id__in=user_ids)
        if not users:
            return MyResponse.failed(message="用户信息不存在")

        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return MyResponse.failed(message="当前班级不存在")

        # 查询在班级中的用户
        user_classes = UserClass.objects.filter(
            class_info=class_obj,
            user_id__in=user_ids
        )

        existing_user_ids = set(uc.user_id for uc in user_classes)

        if not existing_user_ids:
            return MyResponse.success(data={
                "success_count": 0,
                "failed_count": len(user_ids),
                "failed_list": [{"user_id": uid, "reason": "用户不在班级中"} for uid in user_ids]
            })

        with transaction.atomic():
            # 批量删除
            deleted_count, _ = user_classes.delete()

            # 修改用户表的班级id为null
            User.objects.filter(id__in=existing_user_ids).update(class_id=None)

        # 找出删除失败的用户（不在班级中的用户）
        failed_ids = set(user_ids) - existing_user_ids

        response_data = {
            "success_count": deleted_count,
            "failed_count": len(failed_ids),
            "failed_list": [{"user_id": uid, "reason": "用户不在班级中"} for uid in failed_ids]
        }

        logger.info(f"用户 {payload.get('username')} 移除班级成员成功，班级: {class_obj.name}，成功: {deleted_count}，失败: {len(failed_ids)}")
        # 清除班级列表缓存
        cache_delete_pattern("class:list:*")
        # 清除班级统计缓存
        cache_delete_pattern("class:statistics:*")
        # 清除班级成员列表缓存
        cache_delete_pattern("class:members:*")
        # 清除班级排名缓存
        cache_delete_pattern("class:ranking:*")
        # 清除班级成绩趋势缓存
        cache_delete_pattern("class:trend:*")
        # 清除班级相关缓存
        # 清除教师班级缓存
        cache_delete_pattern("teacher:class:*")
        # 清除学生班级信息缓存
        cache_delete_pattern("user:class:*")
        # 清除统计缓存
        cache.delete(CACHE_KEY_USER_STATISTICS)
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
        # 清除学生班级信息缓存
        for user_id in existing_user_ids:
            cache.delete(generate_cache_key(CACHE_KEY_STUDENT_CLASS, user_id=user_id))

        return MyResponse.success(data=response_data)



class ClassAvailableStudentsView(APIView):
    @check_permission
    def get(self, request, class_id):
        payload = request.user

        # 获取未添加班级的学生或老师
        students = User.objects.filter(~Q(role="admin"), class_id=None)

        # 获取筛选字段后的学生信息
        keyword = request.GET.get("keyword", "")
        if keyword:
            students = students.filter(Q(username__icontains=keyword) | Q(nickname__icontains=keyword))

        response_data = []

        for student in students:
            response_data.append({
                "id": student.id,
                "username": student.username,
                "nickname": student.nickname,
                "role": student.role,
                "status": student.status
            })
        return MyResponse.success(data=response_data)



class ClassExamRankingView(APIView):
    @check_permission
    def get(self, request, class_id):
        payload = request.user

        request_data = request.GET
        # print(request_data)
        exam_id = request_data.get("exam_id")

        page = int(request_data.get("page", 1))
        page_size = int(request_data.get("size", 10))
        offset = (page - 1) * page_size

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_CLASS_RANKING, class_id=class_id, exam_id=exam_id, page=page, size=page_size)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 获取班级信息
        class_obj = Class.objects.get(id=class_id)
        response_data = {
            "class_id": class_id,
            "class_name": class_obj.name,
            "exam_id": exam_id,
            "exam_title": None,
            "average_score": 0,
            "pass_rate": 0,
            "list": [],
            "total": 0,
            "page": page,
            "size": page_size
        }
        # 判断考试信息是否存在
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return MyResponse.success(message="考试信息不存在", data=response_data)

        response_data["exam_title"] = exam.title

        # 获取班级学生id
        cur_class_students = User.objects.filter(
            userclass__class_info_id=class_id,
            role="student",
            status=1
        ).select_related('userclass')

        cur_class_student_ids = [s.id for s in cur_class_students]

        # 获取班级学生的这次考试记录信息
        cur_exam_record = ExamRecord.objects.filter(exam_id=exam_id, user_id__in=cur_class_student_ids, status="graded").select_related("user")
        if not cur_exam_record.exists():
            return MyResponse.success(data=response_data)
        # print(cur_exam_record)

        # 获取这场考试该班级的平均成绩和通过率
        cur_exam_state = cur_exam_record.aggregate(
            average_score=Avg("score"),
            pass_rate=Avg(Case(
                When(is_passed=1, then=1.0),
                When(is_passed=0, then=0.0),
                default=None,
                output_field=FloatField()
            ))
        )

        response_data["average_score"] = round(cur_exam_state["average_score"] or 0, 2)
        response_data["pass_rate"] = round(cur_exam_state["pass_rate"] or 0, 2)

        # 分组获取每一个学生的成绩信息
        user_score_list = cur_class_students.filter(examrecord__exam_id=exam_id).annotate(
            max_score=Max("examrecord__score"),
            avg_score=Avg("examrecord__score"),
            pass_rate=Avg(Case(
                When(examrecord__is_passed=1, then=1.0),
                When(examrecord__is_passed=0, then=0.0),
                default=None,
                output_field=FloatField()
            )),
            submit_time=Max("examrecord__submit_time")
        ).values("id", "username", "nickname", "max_score", "avg_score", "pass_rate", "submit_time").order_by("-max_score")
        # print(user_score_list)

        rank_list = []
        for index, student in enumerate(user_score_list, 1):
            # 获取最高分的考试记录，判断是否及格
            best_record = ExamRecord.objects.filter(
                exam_id=exam_id,
                user_id=student["id"],
                score=student["max_score"]
            ).values("is_passed").first()

            data = {
                "rank": index,
                "user_id": student["id"],
                "username": student["username"],
                "nickname": student["nickname"],
                "score": round(student["max_score"], 2) if student["max_score"] is not None else 0,
                "is_passed": best_record["is_passed"] if best_record else 0,
                "submit_time": student["submit_time"].strftime("%Y-%m-%d %H:%M:%S") if student["submit_time"] else "",
            }

            rank_list.append(data)

        total = len(rank_list)
        rank_list_page = rank_list[offset:offset+page_size]
        response_data["list"] = rank_list_page

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_CLASS_RANKING))

        return MyResponse.success(data=response_data)



class ClassScoreTrendView(APIView):
    @check_permission
    def get(self, request, class_id):
        payload = request.user

        request_data = request.GET

        # 获取该班级关联的day天前的试卷id
        days = int(request_data.get("days", 7))
        # 获取当前本地时间
        current_time = timezone.localtime()
        # 计算days天前的时间
        days_ago_time = current_time - timedelta(days=days)
        # 获取班级信息

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_CLASS_TREND, class_id=class_id, days=days)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        class_obj = Class.objects.get(id=class_id)
        response_data = {
            "class_id": class_id,
            "class_name": class_obj.name,
            "total_exams": 0,
            "average_score": 0,
            "highest_average": 0,
            "lowest_average": 0,
            "pass_rate": 0,
            "trend": [],
        }


        cur_class_exam = Exam.objects.filter(
            status='published',
            end_time__gte=days_ago_time,
            examclass__class_info__id=class_id,
        )
        if not cur_class_exam.exists():
            return MyResponse.success(data=response_data)
        # 获取试卷id, 构建试卷映射
        cur_class_exam_ids = [ce.id for ce in cur_class_exam]
        cur_class_exam_map = {
            ce.id: {
                "date": ce.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "exam_title": ce.title,
            }
            for ce in cur_class_exam
        }
        total_exams = cur_class_exam.count()
        response_data["total_exams"] = total_exams
        # 计算每一个试卷的平均分和及格率
        class_exam_state = ExamRecord.objects.filter(exam_id__in=cur_class_exam_ids, status="graded").values("exam_id").annotate(
            average_score=Avg("score"),
            highest_score=Max("score"),
            lowest_score=Min("score"),
            pass_rate=Avg(Case(
                When(is_passed=1, then=1.0),
                When(is_passed=0, then=0.0),
                default=None,
                output_field=FloatField()
            ))
        )
        average_score = 0
        highest_average = 0
        lowest_average = 0
        pass_rate = 0

        for exam_state in class_exam_state:
            average_score += exam_state["average_score"]
            highest_average += exam_state["highest_score"]
            lowest_average += exam_state["lowest_score"]
            pass_rate += exam_state["pass_rate"]
            eid = exam_state["exam_id"]
            response_data["trend"].append({
                "date": cur_class_exam_map[eid]["date"],
                "exam_title": cur_class_exam_map[eid]["exam_title"],
                "average_score": exam_state["average_score"],
                "pass_rate": exam_state["pass_rate"],
            })

        response_data["average_score"] = round(average_score / total_exams or 0, 2)
        response_data["highest_average"] =  round(highest_average / total_exams or 0, 2)
        response_data["lowest_average"] = round(lowest_average / total_exams or 0, 2)
        response_data["pass_rate"] = round(pass_rate / total_exams or 0, 2)

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_CLASS_TREND))
        return MyResponse.success(data=response_data)