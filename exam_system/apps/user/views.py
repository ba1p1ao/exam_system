import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from exam_system.settings import JWT_EXPIRE_TIME
from apps.user.models import User
from apps.user.serializers import UserSerializers, UserUpdateSerializer
from django.core.cache import cache
from utils.CacheConfig import generate_cache_key, CACHE_KEY_USER_INFO
from utils.ResponseMessage import MyResponse
from utils.PasswordEncode import verify_password, hash_password
from utils.JWTAuth import create_token
from utils.CacheConfig import (
    CACHE_KEY_SYSTEM_STATISTICS,
    CACHE_KEY_USER_LOGIN_LOCK,
    CACHE_TIMEOUT_USER_LOGIN_LOCK,
    CACHE_KEY_USER_LOGIN_FAIL_COUNT,
    CACHE_TIMEOUT_USER_LOGIN_FAIL_COUNT,
    get_cache_timeout, generate_filter_key, generate_cache_key)

logger = logging.getLogger('apps')


class UserLoginView(APIView):
    # 登录接口不需要认证
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return MyResponse.failed("用户名和密码不能为空")

        # 检测账户是否被锁定, 如果大于等于5次，视为锁定
        lock_key = generate_cache_key(CACHE_KEY_USER_LOGIN_LOCK, username=username)
        is_locked = cache.get(lock_key)
        if is_locked:
            return MyResponse.failed(f"账户已锁定，请 30 分钟后再试")

        try:
            user = User.objects.get(username=username, status=1)
        except User.DoesNotExist:
            logger.warning(f"登录失败: 用户名 {username} 不存在")
            return MyResponse.failed("用户名或密码错误")

        if not verify_password(password, user.password):
            logger.warning(f"登录失败: 用户 {username} 密码错误")

            # 登录失败之后添加失败次数
            fail_key = generate_cache_key(CACHE_KEY_USER_LOGIN_FAIL_COUNT, username=username)
            fail_count = cache.get(fail_key, 0)
            fail_count += 1
            cache.set(fail_key, fail_count, get_cache_timeout(CACHE_TIMEOUT_USER_LOGIN_FAIL_COUNT))

            if fail_count >= 5:
                cache.set(lock_key, True, get_cache_timeout(CACHE_TIMEOUT_USER_LOGIN_LOCK))
                logger.warning(f"账户 {username} 已锁定，连续失败 5 次")
                return MyResponse.failed("密码错误次数过多，账户已锁定 30 分钟")

            remaining = 5 - fail_count
            return MyResponse.failed(f"用户名或密码错误，剩余尝试次数: {remaining}")

        user_info = UserSerializers(instance=user).data
        token = create_token(payload=user_info, timeout=JWT_EXPIRE_TIME)

        logger.info(f"用户 {username} 登录成功")
        # 如果登录成功，删除锁定缓存
        cache.delete(lock_key)
        return MyResponse.success(message="登录成功", data={
            'token': token,
            'user_info': user_info
        })


class UserInfoView(APIView):
    def get(self, request):
        payload = request.user
        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        username = payload.get("username")
        if not username:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户不存在")

        userinfo = UserSerializers(instance=user).data
        return MyResponse.success(data=userinfo)


class UserRegisterView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        role = request.data.get('role')

        # 验证必填字段
        if not all([username, password, nickname, role]):
            return MyResponse.failed("用户名、密码、昵称和角色不能为空")

        # 验证角色
        if role not in ['student', 'teacher']:
            return MyResponse.failed("角色只能是student或teacher")

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            logger.warning(f"注册失败: 用户名 {username} 已存在")
            return MyResponse.failed("该用户已存在")

        user_serializer = UserSerializers(data=request.data)

        if user_serializer.is_valid():
            user_serializer.save()
            logger.info(f"用户 {username} 注册成功，角色: {role}")
            # 清除系统统计缓存
            cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
            return MyResponse.success(message="注册成功", data={"id": user_serializer.data.get("id")})

        logger.error(f"注册失败: {user_serializer.errors}")
        return MyResponse.failed(message="注册失败", data=user_serializer.errors)


class UserUpdateView(APIView):
    def put(self, request):

        payload = request.user
        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        user_id = payload.get("id")
        if not user_id:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"更新失败: 用户 ID {user_id} 不存在")
            return MyResponse.failed(message="用户不存在")

        user_ser = UserUpdateSerializer(instance=user, data=request.data, partial=True)
        if user_ser.is_valid():
            user_ser.save()
            logger.info(f"用户 {user.username} 信息更新成功")
            cache.delete(generate_cache_key(CACHE_KEY_USER_INFO, user_id=user_id))
            return MyResponse.success(message="更新成功")

        logger.error(f"用户 {user.username} 信息更新失败: {user_ser.errors}")
        return MyResponse.failed(message="更新失败", data=user_ser.errors)


class UserPasswordView(APIView):
    def put(self, request):

        payload = request.user
        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        user_id = payload.get("id")
        if not user_id:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"密码修改失败: 用户 ID {user_id} 不存在")
            return MyResponse.failed(message="用户不存在")

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # 验证必填字段
        if not old_password or not new_password:
            return MyResponse.failed("原密码和新密码不能为空")

        # 验证原密码
        if not verify_password(old_password, user.password):
            logger.warning(f"密码修改失败: 用户 {user.username} 原密码不正确")
            return MyResponse.failed(message="原密码不正确")

        # 更新密码
        user.password = hash_password(new_password)
        user.save()

        logger.info(f"用户 {user.username} 密码修改成功")
        return MyResponse.success(message="密码修改成功")
