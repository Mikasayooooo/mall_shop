from django.shortcuts import render

from rest_framework.views import APIView

import random
from django_redis import get_redis_connection
from mall.libs.yuntongxun.sms import CCP  # 在apps 设置 Sources Root , 就能有代码提示，且不报红
from rest_framework.response import Response

from rest_framework import status

import logging

logger = logging.getLogger('django')


# Create your views here.

class SMSCodeView(APIView):
    '''短信验证码'''

    def get(self, request, mobile):

        # 1.创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')

        # 2.先从redis获取发送标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)

        # 3.如果取到了标记，说明此手机号频繁发送短信
        if send_flag:
            return  Response({'message': '手机频繁发送短信'},status=status.HTTP_400_BAD_REQUEST)

        # 4.生成验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 5.把验证码存储到redis数据库
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)

        # 6.存储一个标记，表示此手机号已经发送过短信,标记有效期60s
        redis_conn.setex('send_flag_%s' %mobile,60,1)

        # 7.利用荣联云通讯发送短信验证码
        # 注意： 测试的短信模板编号为1
        # 参数1: 要给哪个手机发送短信  参数2: ["验证码",有效期]   参数3: 模板编号默认就是1
        # 【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 8.响应
        return Response({'message': 'ok'})
