import logging
from rest_framework.views import APIView
from django.db.models import Count, Q
from apps.user.models import User
from apps.exam.models import Exam, ExamRecord
from apps.question.models import Question
from apps.user.serializers import UserSerializers
from utils.ResponseMessage import check_permission, check_auth, MyResponse
from utils.CacheConfig import (
    CACHE_KEY_USER_INFO,
    CACHE_TIMEOUT_USER_INFO,
    CACHE_KEY_USER_LIST,
    CACHE_TIMEOUT_USER_LIST,
    CACHE_KEY_USER_STATISTICS,
    CACHE_TIMEOUT_USER_STATISTICS,
    CACHE_KEY_SYSTEM_STATISTICS,
    generate_cache_key,
    generate_filter_key,
    get_cache_timeout, CACHE_KEY_STUDENT_CLASS,
)
from utils.CacheTools import cache_delete_pattern
from django.core.cache import cache

logger = logging.getLogger('apps')


class UserListView(APIView):
    @check_permission
    def get(self, request):
        """
        | 参数名 | 类型 | 必填 | 说明 |
        |--------|------|------|------|
        | page | int | 否 | 页码，默认1 |
        | size | int | 否 | 每页数量，默认10 |
        | username | string | 否 | 用户名（模糊搜索） |
        | nickname | string | 否 | 昵称（模糊搜索） |
        | role | string | 否 | 角色：student/teacher/admin |
        | status | int | 否 | 状态：1正常 0禁用 |
        | class_id | int | 否 | 班级ID |
        """
        from apps.classes.models import UserClass, Class

        payload = request.user
        request_data = request.GET

        # 设置过滤参数
        filter_body = {}
        class_id = None
        for k, v in request_data.items():
            if k in ["page", "size"]:
                continue
            elif k == "class_id" and v:
                class_id = int(v)
                filter_body["class_id"] = v
            elif k in ["role", "status"] and v:
                filter_body[f"{k}"] = v
            elif k in ["username", "nickname"] and v:
                filter_body[f"{k}__icontains"] = v

        page = int(request_data.get("page", 1))
        page_size = int(request_data.get("size", 10))
        offset = (page - 1) * page_size

        # 构建缓存键
        cache_filters = generate_filter_key(filter_body)
        cache_key = generate_cache_key(
            CACHE_KEY_USER_LIST, filter=cache_filters, class_id=class_id, page=page, size=page_size
        )
        # 获取缓存数据
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        users = User.objects.filter(**filter_body)

        # 如果有班级筛选，需要通过 UserClass 表来筛选
        if class_id:
            user_ids = UserClass.objects.filter(class_info_id=class_id).values_list('user_id', flat=True)
            users = users.filter(id__in=user_ids)

        total = users.count()
        page_list = users.order_by("-create_time")[offset:offset+page_size]

        if not page_list:
            response_data = {
                "list": [],
                "total": 0,
                "page": page,
                "size": page_size,
            }
            return MyResponse.success(data=response_data)

        ser_data = UserSerializers(instance=page_list, many=True).data

        # 为每个用户添加班级信息
        for user_data in ser_data:
            user_id = user_data["id"]
            try:
                # 获取用户的班级信息
                user_class = UserClass.objects.filter(user_id=user_id).select_related('class_info').first()
                if user_class and user_class.class_info:
                    user_data["class_name"] = user_class.class_info.name
                    user_data["class_id"] = user_class.class_info.id
                else:
                    user_data["class_name"] = None
                    user_data["class_id"] = None
            except Exception as e:
                user_data["class_name"] = None
                user_data["class_id"] = None

        response_data = {
            "list": ser_data,
            "total": total,
            "page": page,
            "size": page_size,
        }

        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_USER_LIST))
        return MyResponse.success(data=response_data)


class UserStatisticsView(APIView):
    @check_permission
    def get(self, request):
        payload = request.user

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_USER_STATISTICS)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        users = User.objects.all()
        total_users = users.count()
        response_data = {
            "total_users": total_users,
            "student_count": 0,
            "teacher_count": 0,
            "admin_count": 0,
            "active_users": 0,
            "disabled_users": 0,
        }
        
        for user in users:
            if user.role == "student":
                response_data["student_count"] += 1
            elif user.role == "teacher":
                response_data["teacher_count"] += 1
            elif user.role == "admin":
                response_data["admin_count"] += 1

            if user.status == 1:
                response_data["active_users"] += 1
            elif user.status == 0:
                response_data["disabled_users"] += 1
        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_USER_STATISTICS))
        return MyResponse.success(data=response_data)
    

class UserInfoView(APIView):
    @check_permission
    def get(self, request, user_id):
        payload = request.user

        # 构建缓存键
        cache_key = generate_cache_key(CACHE_KEY_USER_INFO, user_id=user_id)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户信息不存在")

        ser_user_data = UserSerializers(instance=user).data
        try:
            exam_count = Exam.objects.filter(creator_id=user_id).count()
            question_count = Question.objects.filter(creator_id=user_id).count()
            record_count = ExamRecord.objects.filter(user_id=user_id).count()

            ser_user_data["exam_count"] = exam_count
            ser_user_data["question_count"] = question_count
            ser_user_data["record_count"] = record_count

            # 设置缓存
            cache.set(cache_key, ser_user_data, get_cache_timeout(CACHE_TIMEOUT_USER_INFO))
            return MyResponse.success(data=ser_user_data)
        except Exception as e:
            logger.error(f"获取用户详情失败，用户ID: {user_id}，错误: {e}")
            return MyResponse.failed(f"获取数据出错，{e}")
    
    
    @check_permission
    def delete(self, request, user_id):
        payload = request.user
        admin_username = payload.get("username")

        if user_id == payload.get("id"):
            return MyResponse.failed(message="不能删除自己")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户不存在")

        # 检查用户是否有考试记录
        exam_record_count = ExamRecord.objects.filter(user_id=user_id).count()
        if exam_record_count > 0:
            return MyResponse.failed(message=f"该用户有 {exam_record_count} 条考试记录，无法删除")

        # 检查用户是否是班主任
        from apps.classes.models import Class
        head_teacher_classes = Class.objects.filter(head_teacher_id=user_id).count()
        if head_teacher_classes > 0:
            return MyResponse.failed(message=f"该用户是 {head_teacher_classes} 个班级的班主任，无法删除")

        # 检查用户创建的试卷数量
        exam_count = Exam.objects.filter(creator_id=user_id).count()
        if exam_count > 0:
            return MyResponse.failed(message=f"该用户创建了 {exam_count} 个试卷，无法删除")

        # 检查用户创建的题目数量
        question_count = Question.objects.filter(creator_id=user_id).count()
        if question_count > 0:
            return MyResponse.failed(message=f"该用户创建了 {question_count} 道题目，无法删除")

        # 删除用户的班级关联
        from apps.classes.models import UserClass
        UserClass.objects.filter(user_id=user_id).delete()

        # 删除用户
        delete_count = User.objects.filter(id=user_id).delete()
        if not delete_count:
            logger.error(f"删除用户失败，用户ID: {user_id}，用户名: {user.username}")
            return MyResponse.failed("用户删除失败")

        logger.info(f"管理员 {admin_username} 删除用户: {user.username} (ID: {user_id})")
        # 清除用户列表缓存
        cache_delete_pattern("user:list:*")
        # 清除用户详情缓存
        cache.delete(generate_cache_key(CACHE_KEY_USER_INFO, user_id=user_id))
        # 删除用户统计缓存
        cache.delete(generate_cache_key(CACHE_KEY_USER_STATISTICS))
        cache_delete_pattern("class:members:*")
        # 清除系统统计缓存
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
        return MyResponse.success("用户删除成功")


class UserUpdateStatusView(APIView):
    @check_permission
    def put(self, request, user_id):
        payload = request.user
        admin_username = payload.get("username")

        if user_id == payload.get("id"):
            return MyResponse.failed(message="当前状态下不能修改自己的状态")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户不存在")

        old_status = user.status
        status = request.data.get("status", 0)
        status_text = "正常" if status == 1 else "禁用"

        update_count = User.objects.filter(id=user_id).update(status=status)
        if not update_count:
            logger.error(f"修改用户状态失败，用户ID: {user_id}，用户名: {user.username}")
            return MyResponse.failed(message="修改用户状态失败")

        logger.info(f"管理员 {admin_username} 修改用户状态: {user.username} -> {status_text}")
        # 清除用户列表缓存
        cache_delete_pattern("user:list:*")
        # 清除用户详情缓存
        cache.delete(generate_cache_key(CACHE_KEY_USER_INFO, user_id=user_id))
        # 删除用户统计缓存
        cache.delete(generate_cache_key(CACHE_KEY_USER_STATISTICS))
        cache_delete_pattern("class:members:*")

        return MyResponse.success("修改用户状态成功")


class UserUpdateRoleView(APIView):
    @check_permission
    def put(self, request, user_id):
        payload = request.user
        admin_username = payload.get("username")

        if user_id == payload.get("id"):
            return MyResponse.failed(message="当前状态下不能修改自己的角色")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户不存在")

        old_role = user.role
        role = request.data.get("role", 0)
        role_map = {'student': '学生', 'teacher': '教师', 'admin': '管理员'}

        update_count = User.objects.filter(id=user_id).update(role=role)
        if not update_count:
            logger.error(f"修改用户角色失败，用户ID: {user_id}，用户名: {user.username}")
            return MyResponse.failed(message="修改用户角色失败")

        logger.info(f"管理员 {admin_username} 修改用户角色: {user.username} -> {role_map.get(role, role)}")
        # 清除用户列表缓存
        cache_delete_pattern("user:list:*")
        # 清除用户详情缓存
        cache.delete(generate_cache_key(CACHE_KEY_USER_INFO, user_id=user_id))
        # 删除用户统计缓存
        cache.delete(generate_cache_key(CACHE_KEY_USER_STATISTICS))
        # 清除班级成员缓存
        cache_delete_pattern("class:members:*")
        # 清除学生班级信息缓存
        cache.delete(generate_cache_key(CACHE_KEY_STUDENT_CLASS, user_id=user_id))

        return MyResponse.success("修改用户角色成功")
    
    
    