from django.db import models
from django.conf import settings
from apps.user.models import User
from apps.question.models import Question
from apps.exam.models import ExamRecord

class Mistake(models.Model):
    """
    使用外键关联的版本
    """

    class Meta:
        db_table = 'mistake'
        verbose_name = '错题记录'
        verbose_name_plural = '错题记录'
        indexes = [
            models.Index(fields=['user', 'question'], name='idx_user_question'),
            models.Index(fields=['user', 'is_mastered'], name='idx_user_mastered'),
        ]
        unique_together = ['user', 'question']

    MASTERED_CHOICES = [
        (0, '未掌握'),
        (1, '已掌握'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        verbose_name='用户'
    )
    question = models.ForeignKey(
        Question,  # 题目模型
        on_delete=models.CASCADE,
        db_column="question_id",
        verbose_name='题目'
    )
    exam_record = models.ForeignKey(
        ExamRecord,  # 考试记录模型名
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="exam_record_id",
        verbose_name='考试记录'
    )
    mistake_count = models.IntegerField(default=1, verbose_name='错误次数')
    is_mastered = models.IntegerField(choices=MASTERED_CHOICES, default=0, verbose_name='是否已掌握')
    mastered_time = models.DateTimeField(null=True, blank=True, verbose_name='掌握时间')
    last_mistake_time = models.DateTimeField(null=True, blank=True, verbose_name='最后错误时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"错题记录 {self.id}: {self.user.username} - {self.question.content}"