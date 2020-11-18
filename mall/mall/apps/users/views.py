from django.shortcuts import render
from rest_framework import request, status
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView

from .serializers import CreateUserSerializer,UserDetailSerializer,EmailSerializer

from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
            'count':count   # 响应count,一个数字,是因为后端响应要快,不能让用户等,错误信息展示交给前端完成,值需要判断一下
        }

        # 响应
        return Response(data)



class MobileCountView(APIView):
    '''判断手机号是否已经注册'''

    def get(self,request,mobile):
        # 查询user表
        count = User.objects.filter(mobile=mobile).count()

        # 包装响应数据
        data = {
            'mobile':mobile,
            'count':count  # 响应count,一个数字,是因为后端响应要快,不能让用户等,错误信息展示交给前端完成,值需要判断一下
        }

        # 响应
        return Response(data)



# GET /user/
class UserDetailView(RetrieveAPIView):
    '''用户详细信息展示'''

    serializer_class = UserDetailSerializer
    # queryset = User.objects.all()  现在省略pk,重写get_object()方法,减少数据库查询

    # 指定权限,只有通过认证的用户才能访问当前视图
    permission_classes = [IsAuthenticated]

    def get_object(self):
        '''重写此方法返回 要展示的用户模型对象'''
        return self.request.user



# PUT /email/
class EmailView(UpdateAPIView):
    '''更新用户邮箱'''

    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user



class EmailVerifyView(APIView):
    '''激活用户邮箱'''

    def get(self,request):
        # 1.获取前端查询字符串中传入的token
        token = request.query_params.get('token')

        # 2.把token解密,并查询对应的user
        '''check_verify_email_token的目的就是为了得到user实例对象,如果check_verify_email_token作为实例方法的话,
        需要使用user实例对象来调用,有冲突,所以这里改用 静态方法调用,类方法需要传cls,不需要'''
        user = User.check_verify_email_token(token)

        # 3.修改当前user的email_active为True
        if not user:
            return Response({'message':'激活失败'},status=status.HTTP_400_BAD_REQUEST)

        user.email_active = True
        user.save()

        # 4.响应
        return Response({'message':'激活成功'})
