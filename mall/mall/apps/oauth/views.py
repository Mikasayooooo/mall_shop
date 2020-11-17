from django.shortcuts import render
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response



class QQauthURLView(APIView):
    '''拼接好QQ登录登录网址'''

    def get(self,request):
        # 1.提取前端传入的next参数记录用户从哪里去到login界面
        next = request.query_params('next') or '/'    # drf get获取请求参数query_params

        # if not next:    相当于
        #     next = '/'
        
        # 2.利用QQ登录SDK
        oauth = OAuthQQ()

        # 3.创建QQ登录工具
        login_url = oauth.get_qq_url()

        # 4.调用它里面的方法,拼接好QQ登录网址
        return Response({'login_url':login_url})
