from django.db import models

# 角色枚举定义
ROLE_CHOICES = (
    ('student', '学生'),
    ('teacher', '教师'),
    ('admin', '管理员'),
)

class User(models.Model):
    """用户模型（映射已有的user表）"""
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=255, verbose_name='密码(加密)')
    nickname = models.CharField(max_length=50, null=True, blank=True, verbose_name='昵称')
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name='头像URL')
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='角色'
    )
    class_id = models.IntegerField(null=True, blank=True, verbose_name='班级ID')
    status = models.IntegerField(default=1, verbose_name='状态：1正常 0禁用')
    create_time = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='创建时间')  # 已有表无需auto_now_add
    update_time = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='更新时间')  # 已有表无需auto_now

    class Meta:
        db_table = 'user'  # 必须严格匹配数据库表名
        verbose_name = '用户'
        verbose_name_plural = '用户'
        managed = False  # 关键：告诉Django不管理该表的创建/修改（不会生成迁移文件）
        indexes = [
            models.Index(fields=['username'], name='idx_username'),
            models.Index(fields=['role'], name='idx_role'),
        ]

    def __str__(self):
        return self.username