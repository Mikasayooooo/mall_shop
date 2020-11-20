from rest_framework import serializers
from .models import Area


'''
在查询所有省时用的是AreaSerializer

在查询单一省时 SubsSerializer代表单个省 ----> AreaSerializer 省下面的所有市
在查询单一市时 SubsSerializer代表单个市 ----> AreaSerializer 市下面的所有区

'''


class AreaSerializer(serializers.ModelSerializer):
    '''省的 序列化器'''

    class Meta:
        model = Area
        fields = ['id','name']



class SubsSerializer(serializers.ModelSerializer):
    # 130000
    # 河北省模型.objects.all()
    '''详情视图使用的序列化器'''

    # 进行关联序列化

    # 只会序列化出id,注意:这里必须加上 many=True,read_only=True
    # subs = serializers.PrimaryKeyRelatedField(many=True,read_only=True)

    # 序列化时模型中str方法返回值,注意:这里必须加上 many=True,read_only=True
    # subs = serializers.StringRelatedField(many=True)

    # 注意:这里必须加上 many=True,read_only=True,slug_field 必须为字符串
    # subs = serializers.SlugRelatedField(many=True,read_only=True,slug_field='id')

    subs = AreaSerializer(many=True,read_only=True)

    class Meta:
        model = Area
        fields = ['id','name','subs'] # subs:一生成多的隐式字段


