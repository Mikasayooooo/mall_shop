from django.shortcuts import render
from rest_framework.views import APIView
import random
from django_redis import get_redis_connection
from mall.libs.yuntongxun.sms import CCP  # 在apps 设置 Sources Root , 就能有代码提示，且不报红
from rest_framework.response import Response
from rest_framework import status
import logging
from verifications.captcha.captcha import captcha
from captcha.views import CaptchaStore,captcha_image
import base64
import json


from . import constants
from celery_tasks.sms.tasks import send_sms_code



logger = logging.getLogger('django')




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

        # 创建redis管道：（把多次redis操作装入管道中，将来一次性取执行，减少redis的连接操作，提升redis性能）
        pl = redis_conn.pipeline()

        # 5.把验证码存储到redis数据库
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 6.存储一个标记，表示此手机号已经发送过短信,标记有效期60s
        # redis_conn.setex('send_flag_%s' %mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        pl.setex('send_flag_%s' %mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        # 执行管道
        pl.execute()  # 最后一定要执行，上面代码只是将指令放入到管道中

        # 7.利用荣联云通讯发送短信验证码
        # 注意： 测试的短信模板编号为1
        # 参数1: 要给哪个手机发送短信  参数2: ["验证码",有效期]   参数3: 模板编号默认就是1
        # 【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入

        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        # send_sms_code(mobile,sms_code)  调用普通函数
        send_sms_code.delay(mobile,sms_code)  # 触发异步任务

        # 8.响应
        return Response({'message': 'ok'})





class ImageView(APIView):
    '''生成图片验证码'''

    def get(self,request):
        hashkey = CaptchaStore.generate_key()

        try:
            # 获取id
            id_ = CaptchaStore.objects.filter(hashkey=hashkey).first().id
            image = captcha_image(request,hashkey)  # captcha_image内部是用get获取,需要加异常

            # base64加密
            image_base = base64.b64encode(image.content)
            # json_data = json.dumps({"id":id_,"image_base64":image_base.decode('utf-8')})
            json_data = {"id":id_,"image_base64":image_base.decode('utf-8')}
        except:
            json_data = None

        return Response(json_data)

