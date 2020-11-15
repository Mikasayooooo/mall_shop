from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from .serializers import CreateUserSerializer

from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response

# Create your views here.



class UserView(CreateAPIView):
    '''用户注册'''
    # 指定序列化器
    serializer_class = CreateUserSerializer




class UsernameView(APIView):
    '''判断用户是否已经注册'''

    def get(self,request,username):
        # 查询user表
        count = User.objects.filter(username=username).count()

        # 包装响应数据
        data = {
            'username':username,
            'count':count
        }

        # 响应
        Response(data)



class MobileCountView(APIView):
    '''判断手机号是否已经注册'''

    def get(self,request,mobile):
        # 查询user表
        count = User.objects.filter(mobile=mobile).count()

        # 包装响应数据
        data = {
            'mobile':mobile,
            'count':count
        }

        # 响应
        Response(data)
