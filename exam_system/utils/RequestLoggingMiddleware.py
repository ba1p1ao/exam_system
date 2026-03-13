import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("apps")

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件 - 记录每个请求的详细信息
    """
    def process_request(self, request):
        # 获取用户ip
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')

        # # 获取请求信息
        # request_method = request.method
        # request_path = request.path
        # # 记录请求日志
        # logger.info(
        #     f'请求 | IP: {ip_address}  | 方法: {request_method} | 路径: {request_path}'
        # )

        # 将 IP 地址存入 request 对象，方便后续使用
        request.client_ip = ip_address

        return None

    def process_response(self, request, response):
        # 获取客户端 IP
        ip_address = getattr(request, 'client_ip', 'unknown')

         # 获取请求信息
        request_method = request.method
        request_path = request.path
        request_full_path = request.get_full_path()
        status_code = response.status_code

        # 构造类似 Apache/Nginx 的日志格式
        log_message = f'{ip_address} "{request_method} {request_full_path} HTTP/1.1" {status_code}'
        if status_code >= 500:
            logger.error(log_message)
        elif status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response