from django.shortcuts import render
from rest_framework import request, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView,GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from django_redis import get_redis_connection


from .models import User,Address
from .serializers import CreateUserSerializer,UserDetailSerializer,EmailSerializer,UserAddressSerializer,AddressTitleSerializer,UserBrowerHistorySerializer,SKUSerializer
from goods.models import SKU

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


        if user.email_active:
            return Response({'message':'该邮箱已经激活'})


        user.email_active = True
        user.save()

        # 4.响应
        return Response({'message':'激活成功'})



class AddressViewSet(GenericViewSet):
    '''用户收货地址增删改查'''

    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer
    # queryset =
    def get_queryset(self):
        # return Address.objects.filter(is_deleted=False) 这是查所有用户的地址
        return self.request.user.addresses.filter(is_deleted=False)
        # 这是登录用户的地址


    '''POST /addresses/ 新建 -> create'''
    def create(self,request):
        '''创建地址'''

        # 1.获取user对象
        user = request.user
        # count = user.addresses.all().count()
        count = Address.objects.filter(user=user).count()

        # 2.用户收货地址数量有上限,最多20
        if count > 20:
            return Response({'message':'收货地址数量上限'},status=status.HTTP_400_BAD_REQUEST)

        # 3.创建序列化器进行反序列化
        serializer = self.get_serializer(data=request.data)

        # 4.调用序列化器 的is_valid()
        serializer.is_valid(raise_exception=True)

        # 5.调用序列化器 的save()
        serializer.save()

        # 6.响应
        return Response(serializer.data,status=status.HTTP_201_CREATED)



    '''GET /addresses/ 查询 -> list'''
    def list(self,request):
        '''用户地址列表数据'''

        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset,many=True)
        user = self.request.user  # self 上也有request对象
        return Response({
            'user_id':user.id,
            'default_address_id':user.default_address_id,
            'limit':20,
            'addresses':serializer.data
        })



    '''DELETE /addresses/<pk>/ 删除 -> destroy'''
    def destroy(self,request,pk=None):
        '''删除地址'''

        address = self.get_object()

        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



    # PUT /addresses/<pk>/ 修改 -> update
    '''
参数1：methods：声明该action对应的请求方式，默认GET
参数2：detail：声明该action是否和单一资源对应（传递pk），以及是否是xxx/<pk>/action方法名/格式的请求路径
True：表示请求路径是xxx/<pk>/action方法名/格式
False：表示请求路径是xxx/action方法名/格式
    '''

    '''PUT /addresses/<pk>/title/ 设置标题 -> title'''
    @action(methods=['put'],detail=True)
    def title(self,request,pk=None):
        '''设置标题'''

        address = self.get_object()
        # 这里只修改标题,所以只要传title即可
        serializer = AddressTitleSerializer(instance=address,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



    '''PUT /addresses/<pk>/status/ 设置默认地址 -> status'''
    @action(methods=['put'],detail=True)
    def status(self,request,pk=None):
        '''设置默认地址'''

        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message':'OK'},status=status.HTTP_200_OK)



# CreateAPIView 父类是 GenericAPIView,所以可以把 两个接口写到一起,不需要再定义路由了
# 保存和获取的接口
class UserBrowerHistoryView(CreateAPIView):
    '''用户商品浏览记录'''

    # 指定序列化器
    serializer_class = UserBrowerHistorySerializer
    # 指定用户认证
    permission_classes = [IsAuthenticated]


    def get(self,request):
        '''查询商品浏览记录'''

        # 1.创建redis连接对象
        redis_conn = get_redis_connection('history')

        # 2.获取当前请求的用户
        user = request.user

        # 3.获取redis中当前用户的浏览记录列表数据
        sku_ids = redis_conn.lrange('history_%d' % user.id,0,-1)

        # 4.把sku_id对应的sku模型查询出来
        # SKU.objects.filter(id__in=sku_ids)  不能保证顺序
        sku_list = []
        for sku_id in sku_ids:  # 保证顺序不乱
            sku = SKU.objects.get(id=sku_id)
            # redis的列表,存的都是字符串,取出来时,列表里的数据是bytes类型,所以sku_id 是bytes类型
            sku_list.append(sku)

        # 5.创建序列化器进行序列化
        serializer = SKUSerializer(sku_list,many=True) # 列表也是多,所以也要加many

        # 6.响应
        return Response(serializer.data)
