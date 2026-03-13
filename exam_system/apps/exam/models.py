from django.db import models
from apps.user.models import User
from apps.question.models import Question
from apps.classes.models import Class

# 试卷状态枚举
EXAM_STATUS_CHOICES = (
    ('draft', '草稿'),
    ('published', '已发布'),
    ('closed', '已关闭'),
)

# 考试记录状态枚举
RECORD_STATUS_CHOICES = (
    ('not_started', '未开始'),
    ('in_progress', '进行中'),
    ('submitted', '已提交'),
    ('graded', '已阅卷'),
)

class Exam(models.Model):
    """试卷模型（映射已有的exam表）"""
    title = models.CharField(max_length=100, verbose_name='试卷标题')
    description = models.TextField(null=True, blank=True, verbose_name='试卷描述')
    duration = models.IntegerField(verbose_name='考试时长(分钟)')
    total_score = models.IntegerField(verbose_name='总分')
    pass_score = models.IntegerField(verbose_name='及格分数')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='考试开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='考试结束时间')
    is_random = models.IntegerField(default=0, verbose_name='是否随机组卷：0否 1是')
    allow_retake = models.IntegerField(default=0, verbose_name='是否允许重复作答：0否 1是')
    status = models.CharField(
        max_length=10,
        choices=EXAM_STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='creator_id',
        verbose_name='创建者'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam'
        verbose_name = '试卷'
        verbose_name_plural = '试卷'
        managed = False
        indexes = [
            models.Index(fields=['status'], name='idx_exam_status'),
            models.Index(fields=['creator'], name='idx_exam_creator'),
        ]

    def __str__(self):
        return self.title

class ExamClass(models.Model):
    """试卷班级关联模型"""
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        db_column='exam_id',
        verbose_name='试卷'
    )
    class_info = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        db_column='class_id',
        verbose_name='班级'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'exam_class'
        verbose_name = '试卷班级关联'
        verbose_name_plural = '试卷班级关联'
        managed = False
        unique_together = [['exam', 'class_info']]

    def __str__(self):
        return f'{self.exam.title} - {self.class_info.name}'

class ExamQuestion(models.Model):
    """试卷题目关联模型（映射已有的exam_question表）"""
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        db_column='exam_id',
        verbose_name='试卷'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        db_column='question_id',
        verbose_name='题目'
    )
    sort_order = models.IntegerField(verbose_name='题目排序')

    class Meta:
        db_table = 'exam_question'
        verbose_name = '试卷题目关联'
        verbose_name_plural = '试卷题目关联'
        managed = False
        indexes = [
            models.Index(fields=['exam'], name='idx_exam_question_exam'),
            models.Index(fields=['question'], name='idx_exam_question_question'),
        ]
        unique_together = [['exam', 'question']]  # 匹配数据库的联合唯一约束

    def __str__(self):
        return f'{self.exam.title} - {self.question.content[:20]}'

class ExamRecord(models.Model):
    """考试记录模型（映射已有的exam_record表）"""
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        db_column='exam_id',
        verbose_name='试卷'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='学生'
    )
    score = models.IntegerField(null=True, blank=True, verbose_name='得分')
    is_passed = models.IntegerField(null=True, blank=True, verbose_name='是否及格：0否 1是')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    status = models.CharField(
        max_length=15,
        choices=RECORD_STATUS_CHOICES,
        default='not_started',
        verbose_name='状态'
    )
    is_timeout = models.BooleanField(default=False, verbose_name='是否超时')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始答题时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_record'
        verbose_name = '考试记录'
        verbose_name_plural = '考试记录'
        managed = False
        indexes = [
            models.Index(fields=['exam'], name='idx_exam_record_exam'),
            models.Index(fields=['user'], name='idx_exam_record_user'),
            models.Index(fields=['status'], name='idx_exam_record_status'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.exam.title} - {self.get_status_display()}'

class AnswerRecord(models.Model):
    """答题记录模型（映射已有的answer_record表）"""
    exam_record = models.ForeignKey(
        ExamRecord,
        on_delete=models.CASCADE,
        db_column='exam_record_id',
        verbose_name='考试记录'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        db_column='question_id',
        verbose_name='题目'
    )
    user_answer = models.TextField(null=True, blank=True, verbose_name='用户答案')
    is_correct = models.IntegerField(null=True, blank=True, verbose_name='是否正确：0否 1是')
    score = models.IntegerField(null=True, blank=True, verbose_name='得分')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'answer_record'
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        managed = False
        indexes = [
            models.Index(fields=['exam_record'], name='idx_answer_record_exam_record'),
            models.Index(fields=['question'], name='idx_answer_record_question'),
        ]
        unique_together = [['exam_record', 'question']]

    def __str__(self):
        return f'{self.exam_record} - {self.question.content[:20]}'