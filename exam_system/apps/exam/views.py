import logging
from statistics import mean
import os

from django.utils.duration import duration_string
from rest_framework.views import APIView
from rest_framework import viewsets, generics
from django.db import transaction
from django.db.models import Count, Avg, Case, When, FloatField, Q, Max, Min
from django.http import FileResponse
from django.conf import settings
from apps.exam.models import Exam, ExamRecord, ExamQuestion, AnswerRecord, ExamClass
from apps.user.models import User
from apps.question.models import Question
from apps.classes.models import Class, UserClass
from apps.mistake.models import Mistake
from apps.exam.serializers import AnswersSerializer, ExamRecordListSerializer, ExamRecordDetailSerializer, ExamSerializer, ExamInfoSerializer, ExamRecordAddSerializer, GroupedExamSerializer
from apps.question.serializers import QuestionListSerializers
from utils.ResponseMessage import MyResponse, check_permission, check_auth # 添加认证的装饰器
from utils.ReportPDF import ReportPDFGenerator
from datetime import datetime
from django.utils import timezone
from utils.CacheTools import cache_delete_pattern
from utils.CacheConfig import (
    CACHE_KEY_EXAM_LIST,
    CACHE_TIMEOUT_EXAM_LIST,
    CACHE_KEY_EXAM_DETAIL,
    CACHE_TIMEOUT_EXAM_DETAIL,
    CACHE_KEY_EXAM_AVAILABLE,
    CACHE_TIMEOUT_EXAM_AVAILABLE,
    generate_cache_key, get_cache_timeout,
    generate_filter_key, CACHE_KEY_EXAM_QUESTIONS, CACHE_TIMEOUT_EXAM_QUESTIONS,
    CACHE_KEY_EXAM_RECORD_DETAIL,
    CACHE_TIMEOUT_EXAM_RECORD_DETAIL,
    CACHE_KEY_EXAM_RECORD_STATISTICS,
    CACHE_TIMEOUT_EXAM_RECORD_STATISTICS,
    CACHE_KEY_EXAM_RANKING,
    CACHE_TIMEOUT_EXAM_RANKING,
    CACHE_KEY_SYSTEM_STATISTICS,
    CACHE_TIMEOUT_SYSTEM_STATISTICS, CACHE_KEY_STUDENT_CLASS,
)
from django.core.cache import cache



logger = logging.getLogger('apps')




class ExamListView(APIView):

    @check_permission
    def get(self, request):
        payload = request.user
        filter_body = {}
        request_data = request.GET

        for k, v in request_data.items():
            if k in ["page", "size"]:
                continue
            elif k == "title" and v:
                filter_body["title__icontains"] = v
            elif v:
                filter_body[k] = v

        # 管理员可以看见所有试卷
        if payload.get("role") != "admin":
            filter_body["creator"] = payload.get("id")

        try:
            page = int(request_data.get("page", 1))
            page_size = int(request_data.get("size", 10))
        except (ValueError, TypeError):
            return MyResponse.failed("页码或每页数量格式错误")

        # 验证分页参数
        if page < 1 or page_size < 1:
            return MyResponse.failed("页码和每页数量必须大于0")

        offset = (page - 1) * page_size

        # 构建cache key
        cache_filters = generate_filter_key(filter_body)
        cache_key = generate_cache_key(
            CACHE_KEY_EXAM_LIST, role=payload.get("role"), filter=cache_filters, page=page, size=page_size
        )
        # 获取缓存数据
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        try:
            exam_queryset = Exam.objects.filter(**filter_body).order_by("-update_time")
            total = exam_queryset.count()
            page_list = exam_queryset[offset:offset + page_size]

            exam_ser_data = ExamSerializer(instance=page_list, many=True).data

            response_data = {
                "list": exam_ser_data,
                "total": total,
                "page": page,
                "size": page_size,
            }

            # 添加缓存
            cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_EXAM_LIST))
            return MyResponse.success(data=response_data)

        except Exception as e:
            return MyResponse.failed(f"获取试卷列表失败: {str(e)}")


class ExamAddView(APIView):
    @check_permission
    def post(self, request):
        payload = request.user
        request_data = request.data

        # 验证必填字段
        required_fields = ['title', 'duration', 'total_score', 'pass_score']
        for field in required_fields:
            if not request_data.get(field):
                return MyResponse.failed(f"缺少必填字段: {field}")

        # 验证 question_ids
        question_ids = request_data.get("question_ids")
        if not question_ids or not isinstance(question_ids, list):
            return MyResponse.failed("请提供有效的题目ID列表")

        try:
            user = User.objects.get(id=payload.get("id"))
        except User.DoesNotExist:
            return MyResponse.failed("用户不存在")

        # 处理日期时间（格式：YYYY-MM-DD HH:MM:SS）
        start_time = None
        end_time = None
        start_time_str = request_data.get("start_time")
        end_time_str = request_data.get("end_time")

        if start_time_str:
            try:
                naive_start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                start_time = timezone.make_aware(naive_start_time)
            except ValueError:
                return MyResponse.failed("开始时间格式错误，请使用: YYYY-MM-DD HH:MM:SS")

        if end_time_str:
            try:
                naive_end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                end_time = timezone.make_aware(naive_end_time)
            except ValueError:
                return MyResponse.failed("结束时间格式错误，请使用: YYYY-MM-DD HH:MM:SS")

        # 使用事务确保数据一致性
        try:
            with transaction.atomic():
                # 添加试卷
                exam_data = {
                    'title': request_data.get("title"),
                    'description': request_data.get("description"),
                    'duration': request_data.get("duration"),
                    'total_score': request_data.get("total_score"),
                    'pass_score': request_data.get("pass_score"),
                    'start_time': start_time,
                    'end_time': end_time,
                    'is_random': request_data.get("is_random", 0),
                    'creator': user,
                }
                exam = Exam.objects.create(**exam_data)

                # 验证题目是否存在
                db_questions = Question.objects.filter(id__in=question_ids)
                if db_questions.count() != len(question_ids):
                    return MyResponse.failed("部分题目ID不存在")

                # 添加试卷题目
                for index, question in enumerate(db_questions, 1):
                    ExamQuestion.objects.create(
                        exam=exam, question=question, sort_order=index
                    )

                # 处理班级关联
                class_ids = request_data.get("class_ids")
                if class_ids and isinstance(class_ids, list):
                    # 验证班级是否存在
                    db_classes = Class.objects.filter(id__in=class_ids)
                    if db_classes.count() != len(class_ids):
                        return MyResponse.failed("部分班级ID不存在")

                    # 添加试卷班级关联
                    for cls in db_classes:
                        ExamClass.objects.create(
                            exam=exam,
                            class_info=cls
                        )

                logger.info(f"用户 {user.username} 创建试卷成功: {exam.title}")
                cache_delete_pattern("exam:list:*")
                # 清除系统统计缓存
                cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
                return MyResponse.success(message="试卷添加成功", data={"id": exam.id})

        except Exception as e:
            logger.error(f"用户 {user.username} 创建试卷失败: {str(e)}")
            return MyResponse.failed(f"添加试卷失败: {str(e)}")


class ExamModelViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects
    serializer_class = ExamSerializer
    
    @check_auth
    def get(self, request, pk):
        payload = request.user

        try:
            exam = self.get_queryset().get(id=pk)
        except Exam.DoesNotExist:
            return MyResponse.failed(message="试卷不存在")


        # 构建 cache key
        cache_key = generate_cache_key(
            CACHE_KEY_EXAM_DETAIL, id=pk,
        )
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        try:
            exam_info = ExamInfoSerializer(instance=exam).data
        except Exception as e:
            return MyResponse.failed(message=f"试卷获取失败: {str(e)}")

        # 设置缓存
        cache.set(cache_key, exam_info, get_cache_timeout(CACHE_TIMEOUT_EXAM_DETAIL))
        return MyResponse.success(data=exam_info)
    
    
    @check_permission
    def put(self, request, pk):
        payload = request.user

        # 构建查询条件
        query_filter = {"id": pk}
        if payload.get("role") == "teacher":
            query_filter["creator_id"] = payload.get("id")

        try:
            exam = self.get_queryset().get(**query_filter)
        except Exam.DoesNotExist:
            return MyResponse.failed(message="试卷不存在")


        request_data = request.data.copy()
        question_ids = request_data.get("question_ids")

        # 移除 question_ids 和不允许修改的字段
        request_data.pop("question_ids", None)
        request_data.pop("id", None)
        request_data.pop("creator", None)
        request_data.pop("create_time", None)
        request_data.pop("update_time", None)

        # 处理日期时间
        start_time_str = request_data.get("start_time")
        end_time_str = request_data.get("end_time")

        if start_time_str:
            try:
                naive_start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                request_data["start_time"] = timezone.make_aware(naive_start_time)
            except ValueError:
                return MyResponse.failed("开始时间格式错误，请使用: YYYY-MM-DD HH:MM:SS")

        if end_time_str:
            try:
                naive_end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                request_data["end_time"] = timezone.make_aware(naive_end_time)
            except ValueError:
                return MyResponse.failed("结束时间格式错误，请使用: YYYY-MM-DD HH:MM:SS")

        if not question_ids or not isinstance(question_ids, list):
            return MyResponse.failed("请提供有效的题目ID列表")

        try:
            with transaction.atomic():
                # 更新试卷信息
                for key, value in request_data.items():
                    if hasattr(exam, key):
                        setattr(exam, key, value)
                exam.save()

                # 获取原试卷的题目id
                old_questions = ExamQuestion.objects.filter(exam=exam).values("question_id")
                old_question_ids = [question.get("question_id") for question in old_questions]

                # 排序方便快速查找不同的qid
                old_question_ids.sort()
                question_ids.sort()
                add_qids = []
                del_qids = []

                # 找出需要添加和删除的题目
                for cur_qid in question_ids:
                    if cur_qid not in old_question_ids:
                        add_qids.append(cur_qid)

                for cur_qid in old_question_ids:
                    if cur_qid not in question_ids:
                        del_qids.append(cur_qid)

                # 删除题目
                if del_qids:
                    ExamQuestion.objects.filter(exam=exam, question_id__in=del_qids).delete()

                # 添加题目
                if add_qids:
                    add_questions = Question.objects.filter(id__in=add_qids)
                    if add_questions.count() != len(add_qids):
                        return MyResponse.failed("部分题目ID不存在")

                    # 获取当前最大排序
                    max_sort_obj = ExamQuestion.objects.filter(exam=exam).order_by('-sort_order').first()
                    start_sort = max_sort_obj.sort_order if max_sort_obj else 0

                    for index, question in enumerate(add_questions, 1):
                        ExamQuestion.objects.create(
                            exam=exam,
                            question=question,
                            sort_order=start_sort + index
                        )

                # 处理班级关联
                class_ids = request.data.get("class_ids")
                if class_ids is not None:
                    # 删除旧的班级关联
                    ExamClass.objects.filter(exam=exam).delete()

                    # 添加新的班级关联
                    if class_ids and isinstance(class_ids, list):
                        db_classes = Class.objects.filter(id__in=class_ids)
                        if db_classes.count() != len(class_ids):
                            return MyResponse.failed("部分班级ID不存在")

                        for cls in db_classes:
                            ExamClass.objects.create(
                                exam=exam,
                                class_info=cls
                            )

                logger.info(f"用户 {payload.get('username')} 更新试卷成功: {exam.title}")

                # 修改成功，就删除缓存信息
                cache_key = generate_cache_key(CACHE_KEY_EXAM_DETAIL, id=pk)
                cache.delete(cache_key)
                cache_delete_pattern("exam:list:*")
                cache_delete_pattern("exam:available:*")
                # 如果题目列表发生变化，删除考试题目缓存
                if add_qids or del_qids:
                    cache_delete_pattern("exam:questions:*")
                # 检查班级是否变化
                old_class_ids = set(ExamClass.objects.filter(exam=exam).values_list('class_info_id', flat=True))
                new_class_ids = set(class_ids or [])
                if old_class_ids != new_class_ids:
                    cache_delete_pattern("class:ranking:*")  # 新增
                    cache_delete_pattern("class:trend:*")

            return MyResponse.success("修改成功")

        except Exception as e:
            logger.error(f"用户 {payload.get('username')} 更新试卷失败: {str(e)}")
            return MyResponse.failed(f"修改试卷失败: {str(e)}")


    @check_permission
    def delete(self, request, pk):
        payload = request.user

        try:
            exam = self.get_queryset().get(id=pk, creator_id=payload.get("id"))
        except Exam.DoesNotExist:
            return MyResponse.failed(message="试卷不存在")

        # 检查试卷状态
        if exam.status == "published":
            return MyResponse.failed(message="无法删除正在发布的试卷")

        # 检查是否有考试记录
        if ExamRecord.objects.filter(exam=exam).exists():
            return MyResponse.failed(message="该试卷已有考试记录，无法删除")

        try:
            with transaction.atomic():
                # 先删除关联的题目
                ExamQuestion.objects.filter(exam=exam).delete()

                # 再删除试卷
                exam.delete()

                logger.info(f"用户 {payload.get('username')} 删除试卷成功: {exam.title}")
                # 删除缓存
                cache_key = generate_cache_key(CACHE_KEY_EXAM_DETAIL, id=pk)
                cache.delete(cache_key)
                cache_delete_pattern("exam:list:*")
                cache_delete_pattern("exam:available:*")
                # 清除系统统计缓存
                cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

                return MyResponse.success("删除成功")

        except Exception as e:
            logger.error(f"用户 {payload.get('username')} 删除试卷失败: {str(e)}")
            return MyResponse.failed(f"删除试卷失败: {str(e)}")
        
        

class ExamPublishView(APIView):
    @check_permission
    def put(self, request, pk):
        payload = request.user

        update_count = Exam.objects.filter(id=pk).update(status="published")
        if not update_count:
            return MyResponse.failed(message="修改试卷失败")
        logger.info(f"用户 {payload.get('username')} 发布试卷成功，试卷ID: {pk}")

        # 删除缓存
        cache_key = generate_cache_key(CACHE_KEY_EXAM_DETAIL, id=pk)
        cache.delete(cache_key)
        cache_delete_pattern("exam:list:*")
        cache_delete_pattern("exam:available:*")
        cache_delete_pattern("class:ranking:*")
        cache_delete_pattern("class:trend:*")
        # 清除系统统计缓存
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

        return MyResponse.success(message="修改成功")
    


class ExamCloseView(APIView):
    @check_permission
    def put(self, request, pk):
        payload = request.user
        update_count = Exam.objects.filter(id=pk, creator_id=payload.get("id")).update(status="closed")
        if not update_count:
            return MyResponse.failed(message="修改试卷失败")
        logger.info(f"用户 {payload.get('username')} 关闭试卷成功，试卷ID: {pk}")

        # 删除缓存
        cache_key = generate_cache_key(CACHE_KEY_EXAM_DETAIL, id=pk)
        cache.delete(cache_key)
        cache_delete_pattern("exam:list:*")
        cache_delete_pattern("exam:available:*")
        cache_delete_pattern("class:ranking:*")
        cache_delete_pattern("class:trend:*")
        # 清除系统统计缓存
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

        return MyResponse.success(message="修改成功")
    

class ExamAvailableView(generics.ListAPIView):
    queryset = Exam.objects
    serializer_class = ExamSerializer
    @check_auth
    def list(self, request, *args, **kwargs):
        payload = request.user
        user_id = payload.get("id")

        # 构建 cache key
        cache_key = generate_cache_key(CACHE_KEY_EXAM_AVAILABLE, user_id=user_id)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 不管学生的班级信息，先获取所有的考试信息
        exam_list = self.get_queryset().filter(status="published")

        # 判断学生是否加入了班级
        user_class = UserClass.objects.filter(user_id=payload.get("id"))
        if user_class:
            user_class = user_class.first()
            user_class_id = user_class.class_info.id
            # print(user_class_id)
            exam_list = exam_list.filter(Q(examclass__class_info__id=user_class_id) | Q(examclass__class_info__id=None))
            if not exam_list:
                return MyResponse.success("没有考试内容")
            # print(exam_list)

        # 判断试卷的时间是否结束
        valid_exam_list = []
        # 过滤掉已经结束的考试
        current_time = timezone.now()
        user_id = payload.get("id")

        for exam in exam_list:
            # 检查考试是否已结束
            if exam.end_time and exam.end_time <= current_time:
                continue

            # 检查是否允许重复作答
            if exam.allow_retake == 0:
                # 不允许重复作答，检查学生是否已完成
                completed_record = ExamRecord.objects.filter(
                    exam_id=exam.id,
                    user_id=user_id,
                    status__in=["submitted", "graded"]
                ).exists()
                if completed_record:
                    continue

            valid_exam_list.append(exam)
        
        if not valid_exam_list:
            return MyResponse.success("没有考试内容")
        
        exam_ser_data = self.get_serializer(instance=valid_exam_list, many=True).data

        # 设置缓存
        cache.set(cache_key, exam_ser_data, get_cache_timeout(CACHE_TIMEOUT_EXAM_AVAILABLE))
        return MyResponse.success(data=exam_ser_data)
              


class ExamStartView(generics.CreateAPIView):
    queryset = ExamRecord.objects
    serializer_class = ExamRecordAddSerializer
    @check_auth
    def post(self, request):
        payload = request.user

        exam_id = request.data.get("exam_id")
        user_id = payload.get("id")
        exam = Exam.objects.filter(id=exam_id, status="published").first()
        if not exam:
            return MyResponse.failed(message="该试卷不存在，请联系老师或管理员")

        user = User.objects.filter(id=user_id).first()

        # 检查是否允许重复作答
        if exam.allow_retake == 0:
            # 不允许重复作答，检查是否已完成考试
            completed_record = ExamRecord.objects.filter(
                exam_id=exam_id,
                user_id=user_id,
                status__in=["submitted", "graded"]
            ).first()
            if completed_record:
                return MyResponse.failed("您已完成该考试，不能重复作答")
            
        # 判断该学生是否开始进行该试卷的考试
        exam_record = ExamRecord.objects.filter(exam_id=exam_id, user_id=user_id, status="in_progress").first()
        if exam_record:
            current_time = timezone.localtime()
            exam_start_time = exam.start_time
            exam_end_time = exam.end_time

            if exam_start_time and current_time < exam_end_time:
                return MyResponse.failed("该试卷还未开始，无法进行考试")

            if exam_end_time and current_time >= exam_end_time:
                return MyResponse.failed("该试卷已经结束，无法进行考试")
            else:
                # 使用 timezone.localtime 将 UTC 时间转换为本地时间
                start_time_local = timezone.localtime(exam_record.start_time)
                response_data = {
                    "id": exam_record.id,
                    "exam_id": exam_id,
                    "user_id": user_id,
                    "status": exam_record.status,
                    "start_time": start_time_local.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": exam.duration,  # 考试时长（分钟）
                }
                return MyResponse.success(data=response_data)

        db_data = {
            "exam": exam.id,  # 传入 ID 而不是对象
            "user": user.id,  # 传入 ID 而不是对象
            "status": "in_progress",
            "start_time": timezone.now()
        }
        exam_record_ser = self.get_serializer(data=db_data)
        try:
            if exam_record_ser.is_valid(raise_exception=True):
                exam_record = exam_record_ser.save()
                logger.info(f"学生 {user.username} 开始考试: {exam.title}")

                # 清除可参加考试列表缓存
                cache_delete_pattern("exam:available:*")

                # 使用 timezone.localtime 将 UTC 时间转换为本地时间
                start_time_local = timezone.localtime(exam_record.start_time)
                response_data = {
                    "id": exam_record.id,
                    "exam_id": exam_id,
                    "user_id": user_id,
                    "status": exam_record.status,
                    "start_time": start_time_local.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": exam.duration,  # 考试时长（分钟）
                }
                return MyResponse.success(data=response_data)
        except Exception as e:
            logger.error(f"学生 {user.username} 开始考试失败: {e}")
            return MyResponse.failed(message=f"{e}")

        return MyResponse.failed()
        
        
    
class ExamQuestionsView(APIView):
    @check_auth
    def get(self, request, exam_id):
        payload = request.user

        # 构建 cache key
        cache_key = generate_cache_key(
            CACHE_KEY_EXAM_QUESTIONS, exam_id=exam_id, user_id=payload.get("id")
        )
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        exam = Exam.objects.filter(id=exam_id, status="published").first()
        if not exam:
            return MyResponse.failed(message="该试卷不存在，请联系老师或管理员")

        exam_questions = ExamQuestion.objects.filter(exam_id=exam_id)
        if not exam_questions:
            return MyResponse.failed(message="该试卷没有题目，请联系老师或管理员")

        try:
            questions = [eq.question for eq in exam_questions]
            ser_question_data = QuestionListSerializers(instance=questions, many=True).data

            # 获取当前用户的考试记录ID（如果有进行中的考试）
            exam_record = ExamRecord.objects.filter(
                exam_id=exam_id,
                user_id=payload.get("id"),
                status="in_progress"
            ).first()

            # 如果有进行中的考试，获取已保存的答案
            saved_answers = {}
            if exam_record:
                answer_records = AnswerRecord.objects.filter(exam_record=exam_record)
                for ar in answer_records:
                    saved_answers[ar.question_id] = ar.user_answer

            # 将已保存的答案添加到返回数据中
            response_data = {
                "questions": ser_question_data,
                "exam_record_id": exam_record.id if exam_record else None,
                "saved_answers": saved_answers
            }
            # 设置缓存
            cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_EXAM_QUESTIONS))
            return MyResponse.success(data=response_data)
        except Exception as e:
            return MyResponse.failed(message="该试卷发生错误，请联系老师或管理员")

class ExamAnswerView(APIView):
    """保存答案"""
    @check_auth
    def post(self, request):
        payload = request.user
        request_data = request.data
        exam_record_id = request_data.get("exam_record_id")
        question_id = request_data.get("question_id")
        user_answer = request_data.get("user_answer")

        if not all([exam_record_id, question_id]):
            return MyResponse.failed(message="缺少必填字段")

        try:
            exam_record = ExamRecord.objects.get(id=exam_record_id, user_id=payload.get("id"))
        except ExamRecord.DoesNotExist:
            return MyResponse.failed(message="考试记录不存在")

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return MyResponse.failed(message="题目不存在")

        try:
            with transaction.atomic():
                # 判断是否存在答题记录
                answer_record = AnswerRecord.objects.filter(
                    exam_record_id=exam_record_id,
                    question_id=question_id
                ).first()

                if answer_record:
                    answer_record.user_answer = user_answer
                    answer_record.save()
                else:
                    AnswerRecord.objects.create(
                        exam_record_id=exam_record_id,
                        question_id=question_id,
                        user_answer=user_answer
                    )

                return MyResponse.success(message="答案保存成功")

        except Exception as e:
            return MyResponse.failed(message=f"保存答案失败: {str(e)}")


class ExamSubmitView(APIView):
    """提交试卷"""
    @check_auth
    def post(self, request):
        payload = request.user
        exam_record_id = request.data.get("exam_record_id")

        if not exam_record_id:
            return MyResponse.failed(message="缺少必填字段")

        try:
            exam_record = ExamRecord.objects.get(
                id=exam_record_id,
                user_id=payload.get("id"),
                status="in_progress"
            )
        except ExamRecord.DoesNotExist:
            return MyResponse.failed(message="考试记录不存在或已完成")

        # 验证考试是否超时
        now = timezone.now()
        start_time = exam_record.start_time
        duration_minutes = exam_record.exam.duration

        if start_time:
            elapsed_seconds = int((now - start_time).total_seconds())
            total_seconds = duration_minutes * 60
            if elapsed_seconds > total_seconds:
                # 考试以超时
                exam_record.is_timeout = True
                logger.warning(f"学生 {payload.get('username')} 提交试卷时已超时，超时: {elapsed_seconds - total_seconds}秒")

        try:
            with transaction.atomic():
                # 获取试卷的所有题目
                exam_questions = ExamQuestion.objects.filter(exam=exam_record.exam)
                questions = [eq.question for eq in exam_questions]

                total_score = 0

                # 计算得分 - 从数据库获取已保存的答案
                # 批量获取所有已存在的答题记录
                existing_records = AnswerRecord.objects.filter(
                    exam_record=exam_record
                ).select_related('question')

                # 创建 question_id 到 answer_record 的映射
                records_map = {r.question_id: r for r in existing_records}

                # 批量更新和创建的列表
                records_to_update = []
                records_to_create = []

                for question in questions:
                    answer_record = records_map.get(question.id)

                    if answer_record and answer_record.user_answer:
                        # 判断答案是否正确
                        is_correct = self.check_answer(question, answer_record.user_answer)

                        if is_correct:
                            answer_record.is_correct = 1
                            answer_record.score = question.score
                            total_score += question.score
                        else:
                            answer_record.is_correct = 0
                            answer_record.score = 0
                            # 添加到错题本中
                            try:
                                mistake = Mistake.objects.get(user_id=payload.get("id"), question_id=question.id)
                                # 更新错题记录
                                mistake.mistake_count += 1
                                mistake.exam_record = exam_record
                                mistake.last_mistake_time = timezone.now()
                                mistake.save()
                            except Mistake.DoesNotExist:
                                # 创建新的错题记录
                                Mistake.objects.create(
                                    user_id=payload.get("id"),
                                    question_id=question.id,
                                    mistake_count=1,
                                    exam_record=exam_record,
                                    last_mistake_time=timezone.now()
                                )

                        records_to_update.append(answer_record)
                    # 如果用户没有答题
                    else:
                        records_to_create.append(
                            AnswerRecord(
                                exam_record_id=exam_record_id,
                                question_id=question.id,
                                user_answer="",
                                is_correct=0,
                                score=0,
                            )
                        )
                        # 未作答也视作为错题，添加到错题本中
                        try:
                            mistake = Mistake.objects.get(user_id=payload.get("id"), question_id=question.id)
                            # 更新错题记录
                            mistake.mistake_count += 1
                            mistake.exam_record = exam_record
                            mistake.last_mistake_time = timezone.now()
                            mistake.save()
                        except Mistake.DoesNotExist:
                            # 创建新的错题记录
                            Mistake.objects.create(
                                user_id=payload.get("id"),
                                question_id=question.id,
                                mistake_count=1,
                                exam_record=exam_record,
                                last_mistake_time=timezone.now()
                            )

                # 批量创建未答题的记录
                if records_to_create:
                    AnswerRecord.objects.bulk_create(records_to_create)

                # 批量更新已答题的记录
                if records_to_update:
                    AnswerRecord.objects.bulk_update(
                        records_to_update,
                        ['is_correct', 'score']
                    )

                # 更新考试记录
                exam_record.score = total_score
                exam_record.is_passed = 1 if total_score >= exam_record.exam.pass_score else 0
                exam_record.status = "graded"
                exam_record.submit_time = timezone.localtime()
                exam_record.save()

                logger.info(f"学生 {payload.get('username')} 提交试卷成功: {exam_record.exam.title}，得分: {total_score}")
                # 清除错题本缓存
                cache_delete_pattern("mistake:list:*")
                # 清除可参加考试列表缓存
                cache_delete_pattern("exam:available:*")
                cache_delete_pattern("exam:ranking:*")
                # 清除考试统计缓存
                cache_delete_pattern("exam:statistics:*")
                # 清除班级排名缓存（因为学生成绩变化了）
                cache_delete_pattern("class:ranking:*")
                cache_delete_pattern("class:statistics:*")
                # 清除班级趋势缓存
                cache_delete_pattern("class:trend:*")
                cache.delete(generate_cache_key(CACHE_KEY_STUDENT_CLASS, user_id=payload.get("id")))
                cache_delete_pattern("user:statistics:*")
                # 清除系统统计缓存
                cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

                return MyResponse.success(
                    message="试卷提交成功",
                    data={
                        "id": exam_record.id,
                        "score": total_score,
                        "is_passed": exam_record.is_passed,
                        "status": exam_record.status,
                        "submit_time": exam_record.submit_time.strftime("%Y-%m-%d %H:%M:%S") if exam_record.submit_time else None
                    }
                )
        except Exception as e:
            logger.error(f"学生 {payload.get('username')} 提交试卷失败: {str(e)}")
            return MyResponse.failed(message=f"提交试卷失败: {str(e)}")

    def check_answer(self, question, user_answer):
        """检查答案是否正确"""
        correct_answer = question.answer.strip().upper()
        user_answer = user_answer.strip().upper()

        if question.type == "single":
            return correct_answer == user_answer
        elif question.type == "multiple":
            # 多选题：答案完全匹配（顺序可能不同）
            correct_answer = correct_answer.replace("[", "").replace("]", "").replace('"', "")
            correct_set = set(correct_answer.split(","))
            user_set = set(user_answer.split(","))
            return correct_set == user_set
        elif question.type == "judge":
            return correct_answer == user_answer
        elif question.type == "fill":
            # 填空题：完全匹配
            return correct_answer == user_answer

        return False


class ExamTimeCheckView(APIView):
    """检查考试剩余时间"""
    @check_auth
    def get(self, request):
        payload = request.user
        exam_record_id = request.GET.get("exam_record_id")

        if not exam_record_id:
            return MyResponse.failed(message="缺少考试记录ID")

        try:
            exam_record = ExamRecord.objects.get(
                id=exam_record_id,
                user_id=payload.get("id"),
                status="in_progress",
            )
        except ExamRecord.DoesNotExist:
            return MyResponse.failed(message="考试记录不存在或已结束")

        # 计算剩余时间（使用服务器时间）
        now = timezone.now()
        start_time = exam_record.start_time
        duration_minutes = exam_record.exam.duration

        if not start_time:
            return MyResponse.failed(message="考试开始时间无效")

        # 计算已用时间
        elapsed_seconds = int((now - start_time).total_seconds())
        total_seconds = duration_minutes * 60
        remaining_seconds = max(0, total_seconds - elapsed_seconds)

        response_data = {
            "remaining_time": remaining_seconds,
            "is_expired": remaining_seconds <= 0,
            "server_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        return MyResponse.success(data=response_data)

class ExamRecordListView(APIView):
    @check_auth
    def get(self, request):
        payload = request.user
        request_data = request.GET
        
        # 参数验证
        try:
            page = int(request_data.get("page", 1))
            page_size = int(request_data.get("size", 10))
        except (ValueError, TypeError):
            return MyResponse.failed(message="页码和每页数量必须是整数")
        
        filter_body = {}
        for k, v in request_data.items():
            if k in ["page", "size"]:
                continue
            elif k == "title" and v:
                # 需要关联 exam 表查询
                continue
            elif v:
                filter_body[k] = v

        # 添加userid, 排除老师和管理员
        user_role = payload.get("role") if isinstance(payload, dict) else getattr(payload, 'role', None)
        user_id = payload.get("id") if isinstance(payload, dict) else getattr(payload, 'id', None)
        
        if user_role not in ["teacher", "admin"]:
            filter_body["user_id"] = user_id
        
        offset = (page - 1) * page_size

        try:
            exam_records = ExamRecord.objects.filter(**filter_body).select_related('exam').order_by("-update_time")
            
            # 如果有 title 参数，进行额外的过滤
            title = request_data.get("title", "")
            if title:
                exam_records = exam_records.filter(exam__title__icontains=title)
            
            total = exam_records.count()
            page_list = exam_records[offset:offset + page_size]
            ser_exam_record_data = ExamRecordListSerializer(instance=page_list, many=True).data
            response_data = {
                "list": ser_exam_record_data,
                "total": total,
                "page": page,
                "size": page_size
            }
            return MyResponse.success(data=response_data)
        except Exception as e:
            return MyResponse.failed(f"获取考试记录列表失败: {str(e)}") 

        

class ExamRecordDetailView(APIView):
    @check_auth
    def get(self, request, pk):
        payload = request.user
        user_role = payload.get("role") if isinstance(payload, dict) else getattr(payload, 'role', None)
        user_id = payload.get("id") if isinstance(payload, dict) else getattr(payload, 'id', None)

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_EXAM_RECORD_DETAIL, id=pk)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        try:
            # 老师和管理员可以查看所有考试记录，学生只能查看自己的
            if user_role in ["teacher", "admin"]:
                exam_record = ExamRecord.objects.get(id=pk)
            else:
                exam_record = ExamRecord.objects.get(id=pk, user_id=user_id)
        except ExamRecord.DoesNotExist:
            return MyResponse.failed("考试记录不存在")

        ser_answer_record_data = ExamRecordDetailSerializer(instance=exam_record).data
        # 设置缓存
        cache.set(cache_key, ser_answer_record_data, get_cache_timeout(CACHE_TIMEOUT_EXAM_RECORD_DETAIL))
        return MyResponse.success(data=ser_answer_record_data)

class ExamRecordStatisticsView(APIView):
    @check_permission
    def get(self, request, exam_id):
        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_EXAM_RECORD_STATISTICS, exam_id=exam_id)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 检查考试是否存在
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            return MyResponse.failed("考试不存在")

        # 获取所有已提交的考试记录（包括已提交和已阅卷）
        all_records = ExamRecord.objects.filter(
            exam_id=exam_id,
            status__in=['submitted', 'graded']
        )

        # 统计实际参加人数（去重）
        total_participants = all_records.values('user_id').distinct().count()

        # 只统计已阅卷的记录用于计算分数
        graded_records = all_records.filter(status='graded')

        # 如果没有已阅卷的记录，返回默认值但包含参加人数
        if not graded_records.exists():
            return MyResponse.success(data={
                "total_participants": total_participants,
                "average_score": None,
                "pass_rate": None,
                "max_score": None,
                "min_score": None,
                "question_stats": []
            })

        # 统计考试记录数据
        stats = graded_records.aggregate(
            total_participants=Count('user_id', distinct=True),
            average_score=Avg('score'),
            pass_rate=Avg(
                Case(
                    When(is_passed=1, then=1.0),
                    When(is_passed=0, then=0.0),
                    default=None,
                    output_field=FloatField()
                )
            ),
            max_score=Max('score'),
            min_score=Min('score')
        )
        
        # 一次性统计所有题目的正确率（优化查询）
        question_stats = AnswerRecord.objects.filter(
            exam_record__exam_id=exam_id,
            exam_record__status='graded'
        ).values('question_id').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=1)),
            correct_rate=Avg(
                Case(
                    When(is_correct=1, then=1.0),
                    When(is_correct=0, then=0.0),
                    default=None,
                    output_field=FloatField()
                )
            )
        ).order_by('question_id')
        
        # 格式化题目统计数据
        question_stats_list = [
            {
                "question_id": q['question_id'],
                "correct_rate": round(q['correct_rate'], 2) if q['correct_rate'] else 0
            }
            for q in question_stats
        ]
        
        # 组装返回数据
        response_data = {
            "total_participants": stats['total_participants'],
            "average_score": round(stats['average_score'], 2) if stats['average_score'] else None,
            "pass_rate": round(stats['pass_rate'], 2) if stats['pass_rate'] else None,
            "max_score": stats['max_score'],
            "min_score": stats['min_score'],
            "question_stats": question_stats_list
        }

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_EXAM_RECORD_STATISTICS))
        return MyResponse.success(data=response_data)
       

class GroupedExamRecordListView(APIView):
    @check_permission
    def get(self, request):
        payload = request.user
        # 获取查询参数，添加错误处理
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('size', 10))
        except (ValueError, TypeError):
            return MyResponse.failed(message="页码和每页数量必须是整数")
        
        if page < 1 or page_size < 1:
            return MyResponse.failed(message="页码和每页数量必须大于0")
        
        title = request.GET.get('title', '')
        status = request.GET.get('status', '')
        # 获取学生筛选参数
        student_username = request.GET.get('student_username', '')
        student_nickname = request.GET.get('student_nickname', '')
        student_status = request.GET.get('student_status', '')
        student_is_passed = request.GET.get('student_is_passed', '')
        
        # 构建查询条件
        queryset = Exam.objects.all()
        if payload.get("role") == "teacher":
            queryset = queryset.filter(creator_id=payload.get("id"))

        if title:
            queryset = queryset.filter(title__icontains=title)
        if status:
            queryset = queryset.filter(status=status)
        else:
            # 默认只显示已发布和已关闭的考试
            queryset = queryset.filter(status__in=['published', 'closed'])
        
        # 使用 annotate 添加统计字段，避免 N+1 查询
        queryset = queryset.annotate(
            participant_count=Count(
                'examrecord__user_id',
                filter=Q(examrecord__status='graded'),
                distinct=True  # 去重，统计实际参加人数
            ),
            average_score=Avg('examrecord__score', filter=Q(examrecord__status='graded')),
            pass_rate=Avg(
                Case(
                    When(examrecord__is_passed=1, then=1.0),
                    When(examrecord__is_passed=0, then=0.0),
                    default=None,
                    output_field=FloatField()
                ),
                filter=Q(examrecord__status='graded')
            )
        )
        
        total = queryset.count()
        offset = (page - 1) * page_size
        exams = queryset.order_by('-create_time')[offset:offset + page_size]
        
        try:
            # 传递学生筛选参数到序列化器
            group_exam_data = GroupedExamSerializer(
                instance=exams, 
                many=True,
                context={
                    'student_username': student_username,
                    'student_nickname': student_nickname,
                    'student_status': student_status,
                    'student_is_passed': student_is_passed
                }
            ).data
            response_data = {
                "list": group_exam_data,
                "total": total,
                "page": page,
                "size": page_size,
            }
            return MyResponse.success(data=response_data)
        except Exception as e:
            return MyResponse.failed(message=f"获取考试信息错误，{e}")


class SystemStatisticsView(APIView):
    @check_auth
    def get(self, request):
        # 构建缓存键
        cache_key = CACHE_KEY_SYSTEM_STATISTICS
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 统计题目总数
        question_count = Question.objects.count()

        # 统计试卷总数
        exam_count = Exam.objects.count()

        # 统计考试记录总数
        record_count = ExamRecord.objects.count()

        # 统计用户总数
        user_count = User.objects.count()

        response_data = {
            "question_count": question_count,
            "exam_count": exam_count,
            "record_count": record_count,
            "user_count": user_count
        }

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_SYSTEM_STATISTICS))
        return MyResponse.success(data=response_data)


class ExamRankingView(APIView):
    @check_auth
    def get(self, request, exam_id):
        payload = request.user

        page = int(request.GET.get("page"))
        page_size = int(request.GET.get("size"))
        class_id = request.GET.get("class_id")
        offset = (page - 1) * page_size

        # 构建缓存键
        cache_key = generate_cache_key(
            CACHE_KEY_EXAM_RANKING,
            exam_id=exam_id,
            class_id=class_id or 'all',
            page=page,
            size=page_size
        )
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 获取当前试卷
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return MyResponse.failed(message="试卷不存在")
        
        response_data = {
            "exam_id": exam_id,
            "exam_title": exam.title,
            "list": []
        }
        class_id = request.GET.get("class_id")
        cur_class_students = User.objects.filter(role="student")
        # print(cur_class_students)
        if class_id:
            cur_class_students = User.objects.filter(role="student", userclass__class_info_id=class_id)

        user_score_list = cur_class_students.annotate(
            max_score=Max("examrecord__score", filter=Q(examrecord__exam_id=exam_id)),
        ).values("id", "username", "nickname", "max_score").order_by("-max_score")

        # 只统计真正参加了考试的学生（max_score 不为 null）
        participated_students = user_score_list.filter(max_score__isnull=False)
        response_data["total_participants"] = participated_students.count()

        # print(user_score_list)
        try:
            for index, user_score in enumerate(participated_students, 1):
                exam_record_best = ExamRecord.objects.filter(
                    exam_id=exam_id,
                    user_id=user_score["id"],
                    score=user_score["max_score"]
                ).values("is_passed", "submit_time").first()
                if not exam_record_best:
                    continue
                rank_list_dict = {}          
                rank_list_dict["rank"] = index
                rank_list_dict["user_id"] = user_score["id"]
                rank_list_dict["username"] = user_score["username"]
                rank_list_dict["nickname"] = user_score["nickname"]
                rank_list_dict["score"] = user_score["max_score"]
    
                # 获取学生最高成绩的考试记录
                rank_list_dict["is_passed"] = exam_record_best["is_passed"]
                rank_list_dict["submit_time"] = exam_record_best["submit_time"].strftime("%Y-%m-%d %H:%M:%S")
                if user_score["id"] == payload.get("id"):
                    response_data["my_rank"] = index
                    response_data["my_score"] = user_score["max_score"]
                
                response_data["list"].append(rank_list_dict)

            response_data["list"] = response_data["list"][offset:offset + page_size]
            # 设置缓存
            cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_EXAM_RANKING))
            return MyResponse.success(data=response_data)
        except Exception as e:
            return MyResponse.failed(message="排名信息获取失败")
            
        
class ExamScoreDistributionView(APIView):
    @check_permission
    def get(self, request, exam_id):
        payload = request.user
        # 判断是否存在该试卷
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return MyResponse.failed(message="该试卷记录不存在")

        # 判断这场考试是否有提交记录
        exam_records = ExamRecord.objects.filter(exam_id=exam_id)
        if not exam_records:
            return MyResponse.failed(message="该试卷还没有考试记录")
        total = exam_records.count()
        response_data = {
            "exam_id": exam_id,
            "exam_title": exam.title,
            "distribution": {
                "0-59": 0,
                "60-69": 0,
                "70-79": 0,
                "80-89": 0,
                "90-100": 0
            },
            "total": total
        }

        for er in exam_records:
            if er.score >= 90:
                response_data["distribution"]["90-100"] += 1
            elif er.score >= 80:
                response_data["distribution"]["80-89"] += 1
            elif er.score >= 70:
                response_data["distribution"]["70-79"] += 1
            elif er.score >= 60:
                response_data["distribution"]["60-69"] += 1
            else:
                response_data["distribution"]["0-59"] += 1

        return MyResponse.success(data=response_data)


class ExamQuestionCorrectnessView(APIView):
    @check_permission
    def get(self, request, exam_id):
        payload = request.user
        # 判断是否存在该试卷
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return MyResponse.failed(message="该试卷记录不存在")

        # 获取试卷的题目
        exam_questions = ExamQuestion.objects.filter(exam_id=exam_id).select_related("question")

        # 获取该试卷的考试答题记录
        exam_record_ids = ExamRecord.objects.filter(exam_id=exam_id).values_list("id", flat=True)

        response_data = {
            "exam_id": exam_id,
            "questions": []
        }

        # 获取每个题目的答题情况统计（按题目分组）
        try:
            question_stats = AnswerRecord.objects.filter(
                exam_record_id__in=exam_record_ids
            ).values("question_id").annotate(
                correct_count=Count("id", filter=Q(is_correct=1)),
                incorrect_count=Count("id", filter=Q(is_correct=0)),
                correct_rate=Avg(
                    Case(
                        When(is_correct=1, then=1.0),
                        When(is_correct=0, then=0.0),
                        default=None,
                        output_field=FloatField()
                    )
                )
            )
        except Exception as e:
            return MyResponse.failed(message=f"获取题目答题情况错误，{e}")

        # 构建题目ID到统计数据的映射
        stats_map = {
            stat['question_id']: stat for stat in question_stats
        }

        # 获取 每一个题目的正确率
        for exam_q in exam_questions:
            question = exam_q.question
            stat = stats_map.get(exam_q.question_id, {
                "correct_count": 0,
                "incorrect_count": 0,
                "correct_rate": 0
            })
            response_data["questions"].append({
                "question_id": question.id,
                "question_content": question.content,
                "correct_count": stat["correct_count"],
                "incorrect_count": stat["incorrect_count"],
                "correct_rate": round(stat["correct_rate"] or 0, 2),
            })


        return MyResponse.success(data=response_data)


class ExamReportGenerate(APIView):
    @check_permission
    def post(self, request, exam_id):
        payload = request.user
        # 判断试卷是否存在
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return MyResponse.failed(message="该试卷已不存在")

        # 验证用户权限：只有管理员或试卷创建者可以生成报告
        if payload.get("role") != "admin" and exam.creator_id != payload.get("id"):
            return MyResponse.failed(message="无权限生成该试卷报告")

        # 获取已阅卷的考试记录
        exam_record = ExamRecord.objects.filter(
            exam_id=exam_id,
            status="graded"
        ).select_related("user")

        # 如果没有考试记录，返回提示
        if not exam_record.exists():
            return MyResponse.failed(message="该试卷暂无已阅卷的考试记录")

        response_data = {
            "report_id": exam_id,
            "exam_id": exam_id,
            "exam_title": exam.title,
            "generate_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {},
            "question_analysis": [],
            "recommendations": [],
        }

        # 考试摘要统计
        # 使用 values_list 优化性能
        total_participants = exam_record.values("user_id").distinct().count()
        response_data["summary"]["total_participants"] = total_participants

        # 获取考试的分数信息
        exam_score_state = exam_record.aggregate(
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

        response_data["summary"]["average_score"] = round(exam_score_state["average_score"] or 0, 2)
        response_data["summary"]["pass_rate"] = round(exam_score_state["pass_rate"] or 0, 2)
        response_data["summary"]["highest_score"] = round(exam_score_state["highest_score"] or 0, 2)
        response_data["summary"]["lowest_score"] = round(exam_score_state["lowest_score"] or 0, 2)

        # 题目分析
        try:
            # 获取该试卷的所有题目信息
            exam_questions = ExamQuestion.objects.filter(
                exam_id=exam_id
            ).select_related("question")

            if not exam_questions.exists():
                return MyResponse.failed(message="该试卷暂无题目")

            # 构建题目难度映射
            question_difficulty = {
                eq.question.id: eq.question.difficulty
                for eq in exam_questions
            }
            exam_question_ids = list(question_difficulty.keys())

            # 获取该试卷的考试记录id
            exam_record_ids = list(exam_record.values_list("id", flat=True))

            # 获取答案记录
            answer_records = AnswerRecord.objects.filter(
                exam_record_id__in=exam_record_ids,
                question_id__in=exam_question_ids
            )

            if not answer_records.exists():
                return MyResponse.failed(message="暂无答题记录")

            # 统计每道题的正确率
            question_answer_state = answer_records.values("question_id").annotate(
                correct_rate=Avg(
                    Case(
                        When(is_correct=1, then=1.0),
                        When(is_correct=0, then=0.0),
                        default=None,
                        output_field=FloatField()
                    )
                )
            )

            recommendations = []
            for qas in question_answer_state:
                qid = qas["question_id"]
                qcr = round(qas["correct_rate"] or 0, 2)
                qdl = question_difficulty.get(qid, "medium")

                if qdl == "easy" and qcr < 0.8:
                    recommendations.append(f"题目{qid}为简单难度题，正确率小于80%，建议加强知识点基础的讲解")
                elif qdl == "medium" and qcr < 0.5:
                    recommendations.append(f"题目{qid}为中等难度题，正确率小于50%，建议加强知识点的讲解")
                elif qdl == "hard" and qcr < 0.3:
                    recommendations.append(f"题目{qid}为困难难度题，正确率小于30%，建议加强知识点的讲解")

                response_data["question_analysis"].append({
                    "question_id": qid,
                    "correct_rate": qcr,
                    "difficulty_level": qdl
                })

            # 如果建议少于题目总数的25%，添加默认建议
            if len(recommendations) < len(exam_question_ids) * 0.25:
                recommendations.append("整体成绩良好，继续保持")

            response_data["recommendations"] = recommendations

            # 使用 ReportPDFGenerator 生成 PDF
            pdf_generator = ReportPDFGenerator()
            buffer = pdf_generator.generate_exam_report(
                exam_title=exam.title,
                summary=response_data["summary"],
                question_analysis=response_data["question_analysis"],
                recommendations=recommendations
            )

            # 保存 PDF 文件
            filename = f"exam_{exam_id}_report.pdf"
            pdf_generator.save_pdf(buffer, filename)

            return MyResponse.success(data={
                "report_id": exam_id,
                "exam_id": exam_id,
                "exam_title": exam.title,
                "filename": filename,
                "generate_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": "报告生成成功，可以点击导出下载"
            })

        except Exception as e:
            return MyResponse.failed(message=f"生成报告时出错：{str(e)}")


class ExamReportExport(APIView):
    @check_permission
    def get(self, request, exam_id):
        payload = request.user

        # 验证权限
        if payload.get("role") not in ["admin", "teacher"]:
            return MyResponse.failed(message="无权限导出该试卷报告")

        # 查找报告文件
        report_dir = os.path.join(settings.BASE_DIR, 'static', 'report_pdfs')
        if not os.path.exists(report_dir):
            return MyResponse.failed(message="报告文件不存在")

        # 获取该试卷的报告文件
        files = [f for f in os.listdir(report_dir) if f.startswith(f"exam_{exam_id}_report")]
        if not files:
            return MyResponse.failed(message="该试卷暂无报告文件，请先生成报告")

        # 按文件名排序，获取最新的
        latest_file = sorted(files, reverse=True)[0]
        filepath = os.path.join(report_dir, latest_file)

        # 返回文件
        try:
            file_handle = open(filepath, 'rb')
            response = FileResponse(file_handle, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{latest_file}"'
            return response
        except Exception as e:
            return MyResponse.failed(message=f"导出报告时出错：{str(e)}")


