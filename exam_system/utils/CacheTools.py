from django_redis import get_redis_connection
from utils.CacheConfig import custom_cache_key
import logging

logger = logging.getLogger('apps')


def cache_delete_pattern(pattern):
    """安全删除匹配模式的所有键"""
    try:
        conn = get_redis_connection("default")  # "default" 对应 CACHES 中的配置
        pattern = custom_cache_key(key=pattern, key_prefix="", version=None)
        # 使用 scan_iter 替代 KEYS，避免阻塞
        deleted_count = 0
        for key in conn.scan_iter(match=pattern, count=100):  # count 每次迭代数量
            conn.delete(key)
            deleted_count += 1

        logger.info(f"缓存删除成功，模式: {pattern}，删除数量: {deleted_count}")
        return deleted_count
    except Exception as e:
        logger.error(f"缓存删除失败，模式: {pattern}，错误: {e}")
        return 0