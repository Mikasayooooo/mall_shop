from rest_framework import serializers


from goods.models import SKU
from .models import OrderInfo,OrderGoods



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




class CommitOrderSerializer(serializers.ModelSerializer):
    '''保存订单序列化器'''

    class Meta:
        model = OrderInfo
        # 'address','pay_method' 这两个字段 只做反序列化的输入
        # order_id 只做序列化输出
        # 它们默认都是双向的
        fields = ['address','pay_method','order_id']

        # 只序列化输出，不做反序列化
        read_only_fields = ['order_id']

        extra_kwargs = {
            'address':{'write_only':True},
            'pay_method':{'write_only':True}
        }


    def create(self, validated_data):
        '''保存订单'''

        # 获取当前保存订单时需要的信息
        # 保存订单基本信息 OrderInfo(一)
        # 从redis读取购物车中被勾选的商品信息
        # 遍历购物车中被勾选的商品信息
            #获取sku对象
            # 判断库存
            # 减少库存，增加销量 SKU
            # 修改SKU销量
            # 保存订单商品信息 OrderGood(多)
            # 累加计算总数量和总价
        # 最后加入邮费和保存订单信息
        # 清除购物车中已结算的商品

        pass