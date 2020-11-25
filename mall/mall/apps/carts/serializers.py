from rest_framework import serializers


from goods.models import SKU


class CartSerializer(serializers.Serializer):
    '''购物车序列化器'''

    sku_id = serializers.IntegerField(label='商品id',min_value=1)
    count = serializers.IntegerField(label='购买数据')
    selected = serializers.BooleanField(label='商品勾选状态',default=True)

    def validate_sku_id(self,value):

        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')
