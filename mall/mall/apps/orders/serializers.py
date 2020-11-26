from django.utils.datetime_safe import datetime
from rest_framework import serializers
from decimal import Decimal


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

        # 获取用户对象
        user = self.context['request'].user  # 必须继承genericAPIView或者是它的子类

        # 订单编号: 拿当前时间 + 00001  : 20190414154600 + 000000001
        # 生成订单编号
        # 时间必须是服务器的时间,格式化 %Y%m%d%h%M%S ,yms大写,%s是字符串, 09%d ,向左补齐至9位
        order_id = datetime.now().strftime('%Y%m%d%h%M%S') + '09%d' % user.id

        # 获取前端传入的收货地址
        address = validated_data.get('address')

        # 获取前端传入的支付方式
        pay_method = validated_data.get('pay_method')

        # 订单状态
        status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method ==
        OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        # 保存订单基本信息 OrderInfo(一)
        orderInfo = OrderInfo.objects.create(
            order_id = order_id,
            user = user,
            address = address,
            total_count = 0,   # 订单中商品总数量
            total_amount = Decimal('0.00'),  # 订单总金额
            freight = Decimal('10.00'),
            pay_method = pay_method,
            status = status
        )

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