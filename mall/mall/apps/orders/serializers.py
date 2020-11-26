from rest_framework import serializers


from goods.models import SKU



class CartSKUSerializer(serializers.ModelSerializer):
    '''订单中的商品序列化器'''

    count = serializers.IntegerField(label='商品购买数量')

    class Meta:
        model = SKU
        fields = ['id','name','default_image_url','price','count']



class OrderSettlementSerializer(serializers.Serializer):
    '''订单序列化器'''

    skus = CartSKUSerializer(many=True)
    freight = serializers.DecimalField(label='运费',max_digits=10,decimal_places=2)