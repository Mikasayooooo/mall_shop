from django.shortcuts import render
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response
from rest_framework import status
# 导入dev配置文件
from django.conf import settings   # settings 代表 dev文件对象
from rest_framework_jwt.settings import api_settings
import logging


from oauth.models import OAuthQQUser
from oauth.serializers import QQAuthUserSerializer
from oauth.utils import generate_save_user_token
from carts.utils import merge_cart_cookie_to_redis


logger = logging.getLogger('django')

class QQauthURLView(APIView):
    '''拼接好QQ登录登录网址'''

    def get(self, request):
        # 1.提取前端传入的next参数记录用户从那里去到login界面
        # next = request.query_params.get('next') or '/'
        # get(self, key, default=None):  获取指定key的值,如果获取的key不存在 可以返回default参数的值
        next = request.query_params.get('next', '/')

        # # QQ登录参数
        # QQ_CLIENT_ID = '101514053'
        # QQ_CLIENT_SECRET = '1075e75648566262ea35afa688073012'
        # QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

        # 2.利用QQ登录SDK
        #  创建QQ登录工具对象
        # oauth = OAuthQQ(client_id=appid, client_secret=appkey, redirect_uri=回调域名, state=记录来源)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        #  3.调用它里面的方法 拼接好QQ登录网址
        login_url = oauth.get_qq_url()
        return Response({'login_url': login_url})



class QQAuthUserView(APIView):
    '''QQ登录 成功后的回调处理'''

    def get(self,request):
        # 1.获取前端传入的code
        code = request.query_params.get('code')
        if not code:
            return Response({'message':'缺少code'},status=status.HTTP_400_BAD_REQUEST)

        # 2.创建QQ登录工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)  # 不需要next参数

        try:
            # 3.调用它里面get_access_token(code) 用code响应QQ服务器获取access_token
            access_token = oauth.get_access_token(code)

            # 4.调用它里面get_open_id(access_token) 用access_token响应QQ服务器获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:  # 捕获其他异常
            logging.info(e)  # 输出到终端和日志文件中
            return Response({'message':'QQ服务器不可用'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 5.查询数据库有没有这个openid
        try:
            authQQUserModel = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:

            # 6.如果没有这个openid,没有绑定用户,把openid加密之后响应给前端,让前端先暂存一会,等待绑定时使用
            # access_token是由于前端写错了,本应该是openid
            # 没有绑定openid，无法识别用户，不能使用服务器资源，所以只能将openid传给前端，让前端保存
            # 因为openid是QQ用户的唯一身份标志,直接传前端可见,需要进行加密传输
            access_token_openid = generate_save_user_token(openid)
            return Response({'access_token':access_token_openid})

        else:
            # 7.如果有这个openid,直接代码登录成功,给前端返回JWT状态保存信息
            # 获取到openid 关联的user
            user = authQQUserModel.user  # 通过外键获取user模型对象

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数(生成payload)
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用,生成jwt

            payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
            token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt

            # 响应对象
            response = Response({
                'token':token,
                'username':user.username,
                'user_id':user.user_id
            })

            # 调用合并购物车函数
            # response是个对象，对象是一个可变类型，对它进行改变，它原本就发生了变化，不需要再进行返回
            merge_cart_cookie_to_redis(request,user,response)

            return response


    def post(self,request):
        '''openid绑定用户接口'''

        # 1.创建序列化器进行反序列化
        serializer = QQAuthUserSerializer(data=request.data)

        # 2.调用is_valid()进行校验
        serializer.is_valid(raise_exception=True)

        # 3.调用序列化器的save方法
        user = serializer.save()   # 因为序列化器传入data,说明调用了create()方法,create()方法返回的是个user对象

        # 4.生成JWT状态保存 token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用,生成jwt

        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt

        # 响应对象
        response = Response({
            'token': token,
            'username': user.username,
            'user_id': user.user_id
        })

        # 调用合并购物车函数
        # response是个对象，对象是一个可变类型，对它进行改变，它原本就发生了变化，不需要再进行返回
        merge_cart_cookie_to_redis(request, user, response)

        # 5.响应
        return response
