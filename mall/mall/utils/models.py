from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""
                                     # 拿这条记录创建的时间赋到这个字段上
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
                                        # 记录每一次给这个指定赋值的时间

    # 加着两个字段的目的是为了提升数据库的性能,为了数据的完整性,方便后期对于数据库的维护

    class Meta:
        abstract = True  # 说明是抽象模型类, ⽤于继承使⽤，数据库迁移时不会创建BaseModel的表
