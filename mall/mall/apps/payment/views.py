from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
from django.conf import settings
import os



from orders.models import OrderInfo
from .models import Payment


class PaymentView(APIView):
    '''生成支付链接'''

    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):

        print(order_id)

        # 获取当前的请求用户对象
        user = request.user

        # 校验订单的有效性
        try:
            # 订单是否真实存在,订单是否是用户本人的,订单状态是否是待支付
            order_model = OrderInfo.objects.get(order_id=order_id,user=user,status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message':'订单有误'},status=status.HTTP_400_BAD_REQUEST)


        # ALIPAY_APPID = '2016091900551154'
        # ALIPAY_DEBUG = True
        # ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'

        # 创建alipay SDK中提供的支付对象
        app_private_key_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/alipay_public_key.pem')).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2  加密方式推荐使用RSA2
            debug = settings.ALIPAY_DEBUG,  # 默认False
        )

        # 调用SDK的方法得到支付链接后面的查询参数
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 马上要支付的订单编号
            total_amount=str(order_model.total_amount),  # 支付总金额,它不认识Decimal,所以这里一定要转换类型
            subject='mall_shop %s' % order_id,  # 标题
            return_url="https://www.baidu.com",  # 支付成功后跳转的回调url
        )

        # 拼接好支付链接
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do?order_id=xxx&xxx=abc
        # 沙箱环境支付链接 :  https://openapi.alipaydev.com/gateway.do? + order_string
        # 真实环境支付链接 :  https://openapi.alipay.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        # 响应
        return Response({'alipay_url':alipay_url})



'''
https://www.baidu.com/
?charset=utf-8
&out_trade_no=20201128191926092
&method=alipay.trade.page.pay.return
&total_amount=6509.00
&sign=BJ51AZfIDLf%2B634TEmzW8tSBpd%2BTBeExb93Yb%2FlPNYXzDogs7SvhGDbAJUKBJA5D5eTB7q7Hs1SkHFZltD7KyOn5ntzruLPkNiDog67PWQkbedL3NLy2oMlSVMbW7O2hI5T8W3%2F5v0gnQBm48CEu%2Fl9qND329iwJSdmYTB3vUqMiq9QTEieT8Vm12KwlZgVzKLyZt3ZVvRxmKP9kQcVDszl4ykRqpNa8%2FlYClIISgSuOwtaAq46nQ%2BiVD5vSbOzZL645l%2FsnMGNdBSVvnXLSO4FD3GU%2Bo%2B48Y1b26H1UoFCTOPwJweI9POkiXXUFGsTQ%2BGZibsvy5zMLH%2FDh5RWLXQ%3D%3D
&trade_no=2020112822001490560501351105
&auth_app_id=2016110300789409
&version=1.0
&app_id=2016110300789409
&sign_type=RSA2
&seller_id=2088102181717954
&timestamp=2020-11-28+21%3A01%3A29
'''

class PaymentStatusView(APIView):
    '''修改订单状态,保存支付宝交易号'''

    def put(self,request):

        # 获取前端以查询字符串方式传入的数据
        queryDict = request.query_params

        # 将queryDict类型转成字典(要将中间的sign从里面移除,然后进行验证)
        data = queryDict.dict()
        # data_list = data['alipay_url'].split('&')

        # 要将中间的sign从里面移除
        sign = data.pop('sign')
        # sign = data_list[-1][5:]

        # 创建alipay支付宝对象
        app_private_key_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2  加密方式推荐使用RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认False
        )

        # 调用alipay SDK的 verify 方法进行验证支付结果是否是支付宝传回来的
        # sign 移除后的值 和 sign解析后的值做比较
        # sign 是 sign 移除后的值用私钥进行加密得到的,然后使用支付宝的公钥进行解密,如果两个值相等,则说明是支付宝返回的
        success = alipay.verify(data, sign)
        if success:

            # 取出mall商城订单编号,再取出支付宝交易号
            order_id = data.get('out_trade_no') # mall_shop 订单编号
            trade_no = data.get('trade_no')  # 支付宝交易号

            # 把两个编号绑定到一起存储到mysql
            Payment.objects.create(
                # 没有order模型,因为order是外键,使用order_id
                order_id=order_id,
                trade_id=trade_no
            )

            # 修改支付成功后的订单状态
            OrderInfo.objects.filter(order_id=order_id,status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        else:
            return Response({'message':'非法请求'},status=status.HTTP_403_FORBIDDEN)

        # 把支付宝交易响应回给前端
        return Response({'trade_id':trade_no})