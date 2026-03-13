from rest_framework.views import APIView
from django.db.models import Count, Q
from apps.classes.models import Class, UserClass
from apps.user.models import User
from utils.ResponseMessage import check_permission, check_auth, MyResponse
from django.core.cache import cache
from utils.CacheConfig import (
    CACHE_KEY_CLASS_LIST,
    CACHE_TIMEOUT_CLASS_LIST,
    CACHE_KEY_TEACHER_CLASS,
    get_cache_timeout, generate_cache_key, generate_filter_key, CACHE_TIMEOUT_TEACHER_CLASS
)

class TeacherClassesView(APIView):
    @check_permission
    def get(self, request):
        payload = request.user
        user_id = payload.get("id")

        try:
            teacher = User.objects.get(id=user_id)
            if teacher.role != "teacher":
                return MyResponse.failed(message="当前登录的用户信息，不是教师")
        except User.DoesNotExist:
            return MyResponse.failed(message="当前登录的用户信息不存在，请重新登录")

        request_data = request.GET
        page = int(request_data.get("page", 1))
        page_size = int(request_data.get("size", 10))
        offset = (page - 1) * page_size

        # 获取过滤条件
        filter_body = {}
        for k, v in request_data.items():
            if k in ["page", "size"]:
                continue
            elif k == "name" and v:
                filter_body["name__icontains"] = v
            elif k in ["grade", "status"] and v:
                filter_body[k] = v

        # 生成缓存键
        cache_filters = generate_filter_key(filter_body)
        cache_key = generate_cache_key(CACHE_KEY_TEACHER_CLASS, filter=cache_filters, user_id=user_id, page=page, size=page_size)
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 获取教师管理的班级（作为班主任）
        cur_teacher_classes = Class.objects.filter(head_teacher=teacher, **filter_body)
        total = cur_teacher_classes.count()

        if total == 0:
            return MyResponse.success(data={
                "list": [],
                "total": 0,
                "page": page,
                "size": page_size
            })

        page_list = cur_teacher_classes[offset:offset + page_size]

        response_list = []
        for cur_class in page_list:
            student_count = UserClass.objects.filter(class_info=cur_class, user__role="student").count()
            response_list.append({
                "id": cur_class.id,
                "name": cur_class.name,
                "grade": cur_class.grade,
                "head_teacher_id": cur_class.head_teacher.id,
                "head_teacher_name": cur_class.head_teacher.username,
                "student_count": student_count,
                "status": cur_class.status,
                "create_time": cur_class.create_time.strftime("%Y-%m-%d %H:%M:%S") if cur_class.create_time else None
            })

        response_data = {
            "list": response_list,
            "total": total,
            "page": page,
            "size": page_size
        }
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_TEACHER_CLASS))
        return MyResponse.success(data=response_data)
