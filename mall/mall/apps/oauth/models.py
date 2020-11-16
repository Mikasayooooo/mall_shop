from django.db import models


# 第三方的子上面,自己定义的在下面
from mall.utils.models import BaseModel
from users.models import User


class OAuthQQUser(BaseModel):
    """QQ登录⽤户数据"""
                                # user被删除了,关联的openid也会被删除,级联
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='⽤户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
                 # 对于某一个字段的数据可能需要频繁的查询,可以指定这个选项,增加索引,从而增加查询速度,优化

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录⽤户数据'
        verbose_name_plural = verbose_name
