import random
from urllib.parse import quote


"""
缓存配置文件
定义所有缓存相关的配置和常量
"""

# ============================================
# 缓存时间配置（单位：秒）
# ============================================

# 实时性要求高的缓存（考试相关）
# 添加 0-20 秒的随机数，避免发生雪崩

CACHE_TIMEOUT_EXAM_AVAILABLE = 60     # 可参加考试列表：1分钟
CACHE_TIMEOUT_EXAM_QUESTIONS = 120          # 考试题目：2分钟

# 频繁查询但变更较少的缓存
CACHE_TIMEOUT_QUESTION_LIST = 600           # 题库列表：10分钟
CACHE_TIMEOUT_QUESTION_DETAIL = 300        # 题目详情：5分钟
CACHE_TIMEOUT_EXAM_LIST = 300               # 试卷列表：5分钟
CACHE_TIMEOUT_EXAM_DETAIL = 180             # 试卷详情：3分钟
CACHE_TIMEOUT_USER_INFO = 300               # 用户信息：5分钟
CACHE_TIMEOUT_USER_LIST = 300               # 用户列表：5分钟
CACHE_TIMEOUT_CLASS_LIST = 600              # 班级列表：10分钟
CACHE_TIMEOUT_MISTAKE_LIST = 300            # 错题列表：5分钟

# 统计类数据缓存（计算成本高）
CACHE_TIMEOUT_CLASS_STATISTICS = 900        # 班级统计：15分钟
CACHE_TIMEOUT_CLASS_MEMBERS = 300           # 班级成员：5分钟
CACHE_TIMEOUT_CLASS_TREND = 600             # 班级成绩趋势：10分钟
CACHE_TIMEOUT_CLASS_RANKING = 300           # 班级考试排名：5分钟
CACHE_TIMEOUT_USER_STATISTICS = 600         # 用户统计：10分钟

# 考试记录相关
CACHE_TIMEOUT_EXAM_RECORD_DETAIL = 120      # 考试记录详情：2分钟
CACHE_TIMEOUT_EXAM_RECORD_STATISTICS = 600  # 考试统计：10分钟
CACHE_TIMEOUT_EXAM_RANKING = 300            # 考试排名：5分钟

# 系统统计相关
CACHE_TIMEOUT_SYSTEM_STATISTICS = 300       # 系统统计：5分钟

# 学生相关
CACHE_TIMEOUT_STUDENT_CLASS = 600           # 学生班级信息：10分钟

# 教师相关
CACHE_TIMEOUT_TEACHER_CLASS = 300           # 教师班级列表：5分钟

# 处理空结构超时时间
CACHE_TIMEOUT_EMPTY_RESULT = 60  

# 用户账户锁定时间
CACHE_TIMEOUT_USER_LOGIN_LOCK = 60 * 30     # 用户账户锁定时间: 30分钟
CACHE_TIMEOUT_USER_LOGIN_FAIL_COUNT = 60 * 15     # 用户账户登陆失败次数时间: 15分钟

# ============================================
# 缓存 Key 前缀配置
# ============================================

CACHE_PREFIX_QUESTION = "question"
CACHE_PREFIX_EXAM = "exam"
CACHE_PREFIX_USER = "user"
CACHE_PREFIX_CLASS = "class"
CACHE_PREFIX_TEACHER = "teacher"
CACHE_PREFIX_MISTAKE = "mistake"
CACHE_PREFIX_STATISTICS = "statistics"

# ============================================
# 缓存 Key 模板
# ============================================

# 题目相关
CACHE_KEY_QUESTION_LIST = f"{CACHE_PREFIX_QUESTION}:list:{{filter}}:{{page}}:{{size}}"
CACHE_KEY_QUESTION_DETAIL = f"{CACHE_PREFIX_QUESTION}:detail:{{id}}"

# 试卷相关
CACHE_KEY_EXAM_LIST = f"{CACHE_PREFIX_EXAM}:list:{{role}}:{{filter}}:{{page}}:{{size}}"
CACHE_KEY_EXAM_DETAIL = f"{CACHE_PREFIX_EXAM}:detail:{{id}}"
CACHE_KEY_EXAM_AVAILABLE = f"{CACHE_PREFIX_EXAM}:available:{{user_id}}"
CACHE_KEY_EXAM_QUESTIONS = f"{CACHE_PREFIX_EXAM}:questions:{{exam_id}}:{{user_id}}"

# 考试记录相关
CACHE_KEY_EXAM_RECORD_DETAIL = f"{CACHE_PREFIX_EXAM}_record:detail:{{id}}"
CACHE_KEY_EXAM_RECORD_STATISTICS = f"{CACHE_PREFIX_EXAM}:statistics:{{exam_id}}"
CACHE_KEY_EXAM_RANKING = f"{CACHE_PREFIX_EXAM}:ranking:{{exam_id}}:{{class_id}}:{{page}}:{{size}}"

# 系统统计相关
CACHE_KEY_SYSTEM_STATISTICS = f"{CACHE_PREFIX_STATISTICS}:system"

# 教师相关
CACHE_KEY_TEACHER_CLASS = f"{CACHE_PREFIX_TEACHER}:class:{{filter}}:{{user_id}}:{{page}}:{{size}}"

# 学生相关
CACHE_KEY_STUDENT_CLASS = f"{CACHE_PREFIX_USER}:class:{{user_id}}"

# 用户相关
CACHE_KEY_USER_INFO = f"{CACHE_PREFIX_USER}:info:{{user_id}}"
CACHE_KEY_USER_LIST = f"{CACHE_PREFIX_USER}:list:{{filter}}:{{class_id}}:{{page}}:{{size}}"
CACHE_KEY_USER_STATISTICS = f"{CACHE_PREFIX_STATISTICS}:user"
CACHE_KEY_USER_LOGIN_LOCK = f"{CACHE_PREFIX_USER}:login_lock:{{username}}"
CACHE_KEY_USER_LOGIN_FAIL_COUNT = f"{CACHE_PREFIX_USER}:login_fail_count:{{username}}"

# 班级相关
CACHE_KEY_CLASS_LIST = f"{CACHE_PREFIX_CLASS}:list:{{filter}}:{{page}}:{{size}}"
CACHE_KEY_CLASS_STATISTICS = f"{CACHE_PREFIX_CLASS}:statistics:{{class_id}}"
CACHE_KEY_CLASS_TREND = f"{CACHE_PREFIX_CLASS}:trend:{{class_id}}:{{days}}"
CACHE_KEY_CLASS_RANKING = f"{CACHE_PREFIX_CLASS}:ranking:{{class_id}}:{{exam_id}}:{{page}}:{{size}}"
CACHE_KEY_CLASS_MEMBERS = f"{CACHE_PREFIX_CLASS}:members:{{class_id}}:{{role}}:{{page}}:{{size}}"

# 错题本相关
CACHE_KEY_MISTAKE_LIST = f"{CACHE_PREFIX_MISTAKE}:list:{{user_id}}:{{filter}}:{{page}}:{{size}}"


def get_cache_timeout(base_timeout):
    """获取带随机抖动的缓存超时时间"""
    jitter = random.randint(0, int(base_timeout * 0.1))  # 10% 的随机抖动
    return base_timeout + jitter


# ============================================
# 缓存 Key 生成函数
# ============================================

def generate_cache_key(template: str, **kwargs) -> str:
    """
    生成缓存 Key

    Args:
        template: 缓存 Key 模板
        **kwargs: 替换模板中的占位符

    Returns:
        完整的缓存 Key

    Example:
        generate_cache_key(CACHE_KEY_QUESTION_DETAIL, id=123)
        # 返回: "question:detail:123"
    """
    return template.format(**kwargs)


def generate_filter_key(filter_dict: dict) -> str:
    """
    将过滤条件字典转换为缓存 Key 字符串

    Args:
        filter_dict: 过滤条件字典

    Returns:
        排序后的过滤条件字符串

    Example:
        generate_filter_key({"type": "single", "difficulty": "easy"})
        # 返回: "difficulty=easy&type=single"
    """
    if not filter_dict:
        return "none"

    # 过滤掉值为 None 的键值对
    filtered_dict = {k: v for k, v in filter_dict.items() if v is not None}
    if not filtered_dict:
        return "none"

    # 排序以确保相同的过滤条件生成相同的 key
    sorted_items = sorted(filtered_dict.items())

    # 对过滤条件的值进行 URL 编码
    return "&".join([f"{k}={quote(str(v), safe='')}" for k, v in sorted_items])


# ============================================
# 缓存版本号（用于批量清除缓存）
# ============================================

# 当需要清除某类缓存时，增加版本号即可
CACHE_VERSION = {
    "question": 1,
    "exam": 1,
    "user": 1,
    "class": 1,
    "teacher": 1,
    "mistake": 1,
}

def custom_cache_key(key, key_prefix, version):
    """
    自定义缓存键生成函数
    Args:
        key: 原始缓存键
        key_prefix: Django缓存框架传递的前缀（当前实现中未使用）
        version: Django缓存框架传递的版本号（当前实现中未使用）

    Returns:
        带版本号的缓存键，格式: :{version}:{key}
    """


    if ":" in key:
        module_prefix = key.split(":")[0]
        cache_version = CACHE_VERSION.get(module_prefix, "1")
        return f":{cache_version}:{key}"
    return key