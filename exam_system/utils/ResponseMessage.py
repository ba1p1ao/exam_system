from django.http import JsonResponse


# - `200`: 请求成功
# - `400`: 请求参数错误
# - `401`: 未授权，需要登录
# - `403`: 无权限访问
# - `404`: 资源不存在
# - `500`: 服务器内部错误

# {
#   "code": 200,
#   "message": "success",
#   "data": {}
# }
class MyResponse:
    @staticmethod
    def success(message='请求成功', data=None):
        response_data = {
            "code": 200,
            "message": message,
            "data": data
        }
        return JsonResponse(response_data, safe=False)

    @staticmethod
    def failed(message='不存在', data=None):
        response_data = {
            "code": 404,
            "message": message,
            "data": data
        }
        return JsonResponse(response_data, safe=False)

    @staticmethod
    def other(code=500, message="服务器内部错误", data=None):
        response_data = {
            "code": code,
            "message": message,
            "data": data
        }
        return JsonResponse(response_data, safe=False)


# 添加装饰器
from functools import wraps
def check_permission(view_func):
    """
    装饰器：检查用户是否为教师或管理员
    """
    @wraps(view_func)
    def wapper(self, request, *args, **kwargs):
        payload = request.user

        # 验证 payload 是否存在且为字典
        if not payload or not isinstance(payload, dict):
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        # 验证字段是否完整
        required_fields = ["id", "username", "role", "status"]
        for field in required_fields:
            if field not in payload:
                return MyResponse.other(code=403, message="用户信息不完整，请重新登录")

        if payload.get("status") != 1:
            return MyResponse.other(code=403, message="该账户已被禁用，请联系管理员")

        if payload.get("role") not in ["teacher", "admin"]:
            return MyResponse.other(code=403, message="只有教师和管理员可以访问题库")

        return view_func(self, request, *args, **kwargs)
    return wapper


def check_auth(view_func):
    """
    装饰器：检查用户信息是否过期
    """
    @wraps(view_func)
    def wapper(self, request, *args, **kwargs):
        payload = request.user

        # 验证 payload 是否存在且为字典
        if not payload or not isinstance(payload, dict):
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        # 验证字段是否完整
        required_fields = ["id", "username", "role", "status"]
        for field in required_fields:
            if field not in payload:
                return MyResponse.other(code=403, message="用户信息不完整，请重新登录")

        if payload.get("status") != 1:
            return MyResponse.other(code=403, message="该账户已被禁用，请联系管理员")

        return view_func(self, request, *args, **kwargs)
    return wapper