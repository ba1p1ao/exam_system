from django.db import models
from apps.user.models import User

# 题目类型枚举
QUESTION_TYPE_CHOICES = (
    ('single', '单选'),
    ('multiple', '多选'),
    ('judge', '判断'),
    ('fill', '填空'),
)

# 难度枚举
DIFFICULTY_CHOICES = (
    ('easy', '简单'),
    ('medium', '中等'),
    ('hard', '困难'),
)

class Question(models.Model):
    """题目模型（映射已有的question表）"""
    type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        verbose_name='题目类型'
    )
    category = models.CharField(max_length=50, null=True, blank=True, verbose_name='题目分类')
    content = models.TextField(verbose_name='题目内容')
    options = models.JSONField(null=True, blank=True, verbose_name='选项(JSON格式)')
    answer = models.TextField(verbose_name='正确答案')
    analysis = models.TextField(null=True, blank=True, verbose_name='题目解析')
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name='难度'
    )
    score = models.IntegerField(default=5, verbose_name='题目分值')
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='creator_id',  # 匹配数据库外键字段名
        verbose_name='创建者',
    )
    create_time = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='创建时间')  # 已有表无需auto_now_add
    update_time = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='更新时间')  # 已有表无需auto_now

    class Meta:
        db_table = 'question'
        verbose_name = '题目'
        verbose_name_plural = '题目'
        managed = False  # 禁用Django的表管理
        indexes = [
            models.Index(fields=['type'], name='idx_question_type'),
            models.Index(fields=['category'], name='idx_question_category'),
            models.Index(fields=['creator'], name='idx_question_creator'),
        ]

    def __str__(self):
        return f'{self.get_type_display()}题：{self.content[:20]}'