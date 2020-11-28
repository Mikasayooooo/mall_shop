from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers


from .models import SKU
from .search_indexes import SKUIndex



class SKUSerializer(serializers.ModelSerializer):
    '''sku商品序列化器'''

    class Meta:
        model = SKU
        fields = ['id','name','price','comments','default_image_url']




class SKUSearchSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """

    # 关联序列化
    object = SKUSerializer(read_only=True)  # 新创建一个 object字段

    class Meta:
        index_classes = [SKUIndex]  # 指定模型
        fields = ('text', 'object')  # 指定字段,将object添加到字段中