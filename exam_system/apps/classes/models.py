from django.db import models
from apps.user.models import User


"""
CREATE TABLE `class` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL COMMENT '班级名称',
  `grade` VARCHAR(50) NULL COMMENT '年级',
  `head_teacher_id` INT NULL COMMENT '班主任ID',
  `status` INT DEFAULT 1 COMMENT '状态：1正常 0禁用',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`head_teacher_id`) REFERENCES `user`(`id`),
  UNIQUE KEY `uk_name` (`name`)
) COMMENT='班级表';
"""
class Class(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='班级名称')
    grade = models.CharField(max_length=50, blank=True, null=True, verbose_name='年级')
    head_teacher = models.ForeignKey(
        User,  # 修改为你的User模型路径
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='班主任'
    )
    status = models.IntegerField(default=1, verbose_name='状态')  # 1正常 0禁用
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')

    class Meta:
        db_table = 'class'
        verbose_name = '班级'
        verbose_name_plural = '班级'
        managed = False

    def __str__(self):
        return self.name

"""
CREATE TABLE `user_class` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '用户ID',
  `class_id` INT NOT NULL COMMENT '班级ID',
  `join_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`),
  FOREIGN KEY (`class_id`) REFERENCES `class`(`id`),
  UNIQUE KEY `uk_user_class` (`user_id`, `class_id`)
) COMMENT='用户班级关联表';

"""

class UserClass(models.Model):
    user = models.ForeignKey(
        User,  # 修改为你的User模型路径
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='用户'
    )
    class_info = models.ForeignKey(
        Class,  # Class模型在同一app中，如果是其他app则用'app名.Class'
        on_delete=models.CASCADE,
        db_column='class_id',
        verbose_name='班级'
    )
    join_time = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')

    class Meta:
        db_table = 'user_class'
        verbose_name = '用户班级关联'
        verbose_name_plural = '用户班级关联'
        managed = False
        # 添加唯一约束，确保每个用户只能加入一次同一个班级
        unique_together = ['user', 'class_info']

    def __str__(self):
        return f"{self.user} - {self.class_info}"
