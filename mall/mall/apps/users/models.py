from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    '''自定义用户模型类'''
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    # 模型已经建表,表中已经有数据,后追加的字段必须 要么 有默认值,要么 允许为空,否则就会报错
    eamil_active = models.BooleanField(default=False,verbose_name='邮箱激活状态')

    class Meta:  # 配置数据库表名，及设置模型在admin站点显示的中文名
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
