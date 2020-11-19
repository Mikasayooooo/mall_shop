from django.db import models


# 省市区 基本不会变,不需要继承 basemodel
class Area(models.Model):
    """省区划"""

    name = models.CharField(max_length=20, verbose_name='名称')

    # 注意,自关联的表 外键指向自己本身 self,
    # on_delete=models.SET_NULL  外键允许为空,省不需要父级
    # null=True  数据库里的外键字段为空
    # blank=True  表单里的为空
    # related_name 相当于 flask的relationship,在这个模型里面还隐式的生成一个字段,
    # area_set,而 related_name 把一生成多的隐式字段改成subs
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级⾏政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '⾏政区划'
        verbose_name_plural = '⾏政区划'

    def __str__(self):
        return self.name
