import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.user.models import User
from exam_system.settings import SECRET_KEY
from django.utils import timezone


def create_token(payload: dict, timeout=3600):
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload["exp"] = timezone.now() + timezone.timedelta(seconds=timeout)

    return jwt.encode(headers=header, payload=payload, key=SECRET_KEY, algorithm="HS256")


def get_payload(token):
    """解码并验证JWT Token"""
    result = {"status": False, "payload": None, "error": None}
    try:
        result["payload"] = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": True}  # 确保验证过期时间
        )
        result["status"] = True
    except jwt.ExpiredSignatureError:
        result["error"] = "Token已过期"
    except jwt.InvalidTokenError as e:
        result["error"] = f"无效Token: {e}"
    return result



class JWTHeaderQueryParamAuthentication(BaseAuthentication):
    """从请求头或查询参数中获取JWT Token进行认证"""
    def authenticate(self, request):
        # 从请求头获取token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header:
            # 处理Bearer token格式
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                raise AuthenticationFailed('Token格式错误，应为: Bearer <token>')
            token = parts[1]
        else:
            # 如果请求头中没有，尝试从查询参数获取
            token = request.GET.get("token", "")
            if not token:
                # 如果没有token，返回None让其他认证类处理
                return None

        try:
            # 验证token
            result = get_payload(token)

            # 只返回payload作为user对象，符合DRF标准
            if not result.get("status"):
                raise AuthenticationFailed(result.get("error", "Token验证失败"))

            payload = result.get("payload")

            user_id = payload.get("id")
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    # 检查用户状态
                    if user.status != 1:
                        raise AuthenticationFailed("该账户已被禁用，请联系管理员")

                except User.DoesNotExist:
                    raise AuthenticationFailed("用户不存在")

            # 验证 payload 的完整性
            required_fields = ["id", "username", "role", "status"]
            for field in required_fields:
                if field not in payload:
                    raise AuthenticationFailed(f"Token中缺少必需字段: {field}")

            # 验证字段值的有效性
            if not isinstance(payload.get("id"), int):
                raise AuthenticationFailed("用户ID格式错误")

            if payload.get("role") not in ["student", "teacher", "admin"]:
                raise AuthenticationFailed("用户角色无效")

            if payload.get("status") not in [1, 0]:
                raise AuthenticationFailed("用户状态无效")

            return payload, token

        except AuthenticationFailed as e:
            raise e

    def authenticate_header(self, request):
        return 'Bearer'