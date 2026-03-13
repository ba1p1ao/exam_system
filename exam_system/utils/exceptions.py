from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from utils.ResponseMessage import MyResponse


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    """
    # 调用 DRF 默认的异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        # 自定义响应格式
        return MyResponse.other(
            code=response.status_code,
            message=response.data.get('detail', str(exc))
        )

    # 处理 DRF 未处理的异常
    return MyResponse.other(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=f"服务器内部错误: {str(exc)}"
    )