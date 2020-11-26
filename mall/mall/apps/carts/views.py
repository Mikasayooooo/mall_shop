from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import pickle,base64
from rest_framework import status
from django_redis import get_redis_connection


from .serializers import CartSerializer,SKUCartSerializer,CartDeletedSerializer,CartSelectedAllSerializer
from goods.models import SKU



class CartView(APIView):
    '''购物车增删改查'''

    def perform_authentication(self, request):
        '''重写此方法,直接pass,可以延后认证,延后到第一次通过 request.user或request.auth才去认证'''
        pass

    def post(self,request):
        '''新增'''

        # 1.创建序列化器进行反序列化
        serializer = CartSerializer(data=request.data)

        # 2.调用is_valid进行校验
        serializer.is_valid(raise_exception=True)

        # 3.获取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')


        try:
            # 执行此代码时会执行认证逻辑,如果登录用户认证成功没有异常,但是未登录用户认证会报异常
            user = request.user
        except:
            user = None

        # 创建响应对象 , 将响应放在前面,减少冗余代码
        response = Response(serializer.data,status=status.HTTP_201_CREATED)

        # is_authenticated 判断匿名用户还是 登录用户(判断用户是否通过认证)
        if user and user.is_authenticated:
            '''登录用户新增redis购物车数据'''
            """
               hash: {'sku_id_1': 2, 'sku_id_16':1}
               set: {sku_id_1}
           """

            # 创建redis连接对象
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()  # 创建管道

            # 添加 如果添加到sku_id在hash中已经存在,需要做增量
            # redis_conn.hincrby('cart_%d % user.id, sku_id, count)
            # redis_conn.hincrby('cart_%d % user.id, sku_id_5, 3)
            # 如果要添加的sku_id在hash字典中不存在,就是新增,如果存在,就会自动做增量计数再存储
            pl.hincrby('cart_%d' % user.id,sku_id,count)

            # 把勾选的商品sku_id存储到set集合中
            if selected:
                pl.sadd('selected_%d' % user.id,sku_id)

            # 执行管道
            pl.execute()

            # 响应
            # return Response(serializer.data,status=status.HTTP_201_CREATED)

        else:
            '''非登录用户新增cookie购物车数据'''

            '''
            {
                'sku_id_1': {'count': 1, 'selected': True},
                'sku_id_16': {'count': 1, 'selected': True}
            }
            '''

            # 获取cookie中的购物车数据
            cart_str = request.COOKIES.get('cart') # 所有get获取,不存在返回None
            if cart_str: # 上面之前的cookie购物车里已经有商品
                # 把字符串转换成bytes类型的字符串
                cart_str_bytes = cart_str.encode()

                # 把bytes类型的字符串转换成bytes类型
                cart_bytes = base64.b64decode(cart_str_bytes)

                # 把bytes类型转换成字典
                cart_dict = pickle.loads(cart_bytes)
            else:
                # 如果cookie还没有购物车数据,说明是第一次添加
                cart_dict = {}

            # 增量计数
            if sku_id in cart_dict:
                # 判断当前要添加的sku_id 在字典中是否存在
                origin_count = cart_dict[sku_id]['count']

                # 原购买数据和本次购买数据相加
                # count = origin_count + count
                count += origin_count

            # 把新的商品添加到cart_dict字典中
            # 不存在就新增,存在就赋值修改
            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }


            # 把字典转换成bytes类型
            cart_bytes = pickle.dumps(cart_dict)

            # 把bytes类型转换成bytes类型的字符串
            cart_str_bytes = base64.b64encode(cart_bytes)

            # 把bytes类型的字符串转换成字符串
            cart_str = cart_str_bytes.decode()

            # 使用相同的变量名 作用:
            # 1.减少变量名
            # 2.没有变量取引用数据,就会被垃圾回收机制回收,减少内存占用

            # 创建响应对象
            # response = Response(serializer.data,status=status.HTTP_201_CREATED)
            # 设置cookie
            response.set_cookie('cart',cart_str)

        return response


    def get(self,request):
        '''查询'''

        try:
            user = request.user
        except:
            user = None

        if user and user.is_authenticated:
            '''登录用户获取redis购物车数据'''

            # 创建redis连接对象
            redis_conn = get_redis_connection('cart')

            # 获取hash数据 {sku_id_1: 1, sku_id_16: 2}
            cart_redis_dict = redis_conn.hgetall('cart_%d' % user.id)

            # 获取set集合数据 {sku_id_1}  SMEMBERS
            selecteds = redis_conn.smembers('selected_%d' % user.id)

            # 将redis购物车数据格式转换成和cookie购物车数据格式一致
            cart_dict = {}

            # 遍历hash中的所有键值对
            for sku_id_bytes,count_bytes in cart_redis_dict.items():

                # 包到字典中的数据 ,注意从redis中取出来的数据是 bytes类型,类型转换
                cart_dict[int(sku_id_bytes)] = {
                    'count':int(count_bytes),
                    'selected':sku_id_bytes in selecteds # 着两个都是bytes类型
                }


            pass
        else:
            '''未登录用户获取redis购物车数据'''
            '''
                {
                    'sku_id_1': {'count': 1, 'selected': True},
                    'sku_id_16': {'count': 1, 'selected': True}
                }
            '''

            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            else:
                return Response({'message':'没有购物车数据'},status=status.HTTP_400_BAD_REQUEST)

        #根据sku_id 查询sku模型
        sku_ids = cart_dict.keys()

        # 直接查询出所有的sku模型返回查询集
        skus = SKU.objects.filter(id__in=sku_ids)

        #给每个sku模型多定义一个count和selected属性
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 创建序列化器进行序列化
        serializer = SKUCartSerializer(instance=skus,many=True)

        # 响应
        return Response(serializer.data)


    def put(self,request):
        '''修改'''

        # 1.创建序列化器进行反序列化
        serializer = CartSerializer(data=request.data)

        # 2.调用is_valid进行校验
        serializer.is_valid(raise_exception=True)

        # 3.获取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        try:
            # 执行此代码时会执行认证逻辑,如果登录用户认证成功没有异常,但是未登录用户认证会报异常
            user = request.user
        except:
            user = None

        # 创建响应对象 , 将响应放在前面,减少冗余代码
        response = Response(serializer.data)

        # is_authenticated 判断匿名用户还是 登录用户(判断用户是否通过认证)
        if user and user.is_authenticated:
            '''登录用户修改redis购物车数据'''

            # 创建redis连接对象
            redis_conn = get_redis_connection('cart')

            # 创建管道对象
            pl = redis_conn.pipeline()

            # 覆盖sku_id 对应的count
            pl.hset('cart_%d' % user.id, sku_id, count)

            # 如果勾选,就把勾选的商品sku_id存储到set集合中
            if selected:
                pl.sadd('selected_%d' % user.id, sku_id)
            else:
                # 如果未勾选,就把未勾选的商品sku_id从set集合中移除
                pl.srem('selected_%d' % user.id,sku_id)

            # 执行管道
            pl.execute()

        else:
            '''非登录用户修改cookie购物车数据'''

            # 获取cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')  # 使用get获取,不存在返回None
            if cart_str:  # 上面之前的cookie购物车里已经有商品
                # # 把字符串转换成bytes类型的字符串
                # cart_str_bytes = cart_str.encode()
                #
                # # 把bytes类型的字符串转换成bytes类型
                # cart_bytes = base64.b64decode(cart_str_bytes)
                #
                # # 把bytes类型转换成字典
                # cart_dict = pickle.loads(cart_bytes)

                # 把cookie字符串转换成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                # 如果cookie没有取出,提前响应,不执行后续代码
                return Response({'message':'没有获取到cookie'},status=status.HTTP_400_BAD_REQUEST)

            # 直接覆盖原cookie字典数据
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # # 把字典转换成bytes类型
            # cart_bytes = pickle.dumps(cart_dict)
            #
            # # 把bytes类型转换成bytes类型的字符串
            # cart_str_bytes = base64.b64encode(cart_bytes)
            #
            # # 把bytes类型的字符串转换成字符串
            # cart_str = cart_str_bytes.decode()

            # 使用相同的变量名 作用:
            # 1.减少变量名
            # 2.没有变量取引用数据,就会被垃圾回收机制回收,减少内存占用

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建响应对象
            response = Response(serializer.data)

            # 设置cookie
            response.set_cookie('cart', cart_str)

        return response


    def delete(self,request):
        '''删除'''

        # 1.创建序列化器进行反序列化
        serializer = CartDeletedSerializer(data=request.data)

        # 2.调用is_valid进行校验
        serializer.is_valid(raise_exception=True)

        # 3.获取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')

        try:
            # 执行此代码时会执行认证逻辑,如果登录用户认证成功没有异常,但是未登录用户认证会报异常
            user = request.user
        except:
            user = None

        # 创建响应对象 , 将响应放在前面,减少冗余代码
        response = Response(serializer.data,status=status.HTTP_204_NO_CONTENT)

        # is_authenticated 判断匿名用户还是 登录用户(判断用户是否通过认证)
        if user and user.is_authenticated:
            '''登录用户删除redis购物车数据'''

            # 创建redis连接对象
            redis_conn = get_redis_connection('cart')

            # 创建管道对象
            pl = redis_conn.pipeline()

            # 删除hash数据
            pl.hdel('cart_%d' % user.id, sku_id)  # 不存在不会报错

            # 删除set数据
            pl.srem('selected_%d' % user.id, sku_id)  # 不存在不会报错

            # 执行管道
            pl.execute()

        else:
            '''非登录用户删除cookie购物车数据'''

            # 获取cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')  # 使用get获取,不存在返回None

            if cart_str:  # 上面之前的cookie购物车里已经有商品

                # 把cookie字符串转换成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                # 如果cookie没有取出,提前响应,不执行后续代码
                return Response({'message': '没有获取到cookie'}, status=status.HTTP_400_BAD_REQUEST)

            # 把要删除的sku_id 从cookie大字典中移除键值对
            if sku_id in cart_dict:  # 判断要删除的sku_id 是否存在于字典中,存在再去删除
                # 这里要做 判断,防止sku_id不存在,(商品存在,但不存在购物车里,比如通过postman模拟,就会报错)
                del cart_dict[sku_id]

            # cookie = {}  不是 None
            # 如果删除后只剩下{},就没必要存在了,减少内存,严谨一点,将{}删除
            if len(cart_dict.keys()):

                # 把cookie字典转换成cookie字符串
                cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

                # 设置cookie
                response.set_cookie('cart', cart_str)
            else:
                # 这里要删除cookie,不进行删除,cookie还是没有发生变化
                # cookie 购物车数据已经清空了
                response.delete_cookie('cart')

        return response




class CartSelectedAllView(APIView):
    '''购物车全选'''

    def perform_authentication(self, request):
        '''重写此方法延后认证'''
        pass

    def put(self,request):
        '''购物车全选'''

        try:
            user = request.user
        except:
            user = None

        # 创建序列化器
        serializer = CartSelectedAllSerializer(data=request.data)

        # 校验
        serializer.is_valid(raise_exception=True)

        # 获取校验后的数据
        selected = serializer.validated_data.get('selected')

        # 响应
        response = Response(serializer.data)

        if user and user.is_authenticated:
            '''登录用户修改redis购物车数据'''
        else:
            '''非登录用户修改cookie购物车数据'''

            # 先获取cookie数据
            cart_str = request.COOKIES.get('cart')

            # 判断cookie中购物车数据是否有值
            if cart_str:
                # 把字符串转换成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

            # 如果cookie中没有取出购物车数据
            else:
                return Response({'message':'cookie中 没有购物车数据'},status=status.HTTP_400_BAD_REQUEST)
                # 提前响应

            # 遍历cookie大字典,根据前端传过来的selected来修改商品的选中状态
            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected

            # 再将字典转换成字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 设置cookie
            response.set_cookie('cart',cart_str)

        # 响应
        return response

