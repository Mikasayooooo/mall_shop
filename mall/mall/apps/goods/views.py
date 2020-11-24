from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView


from .models import SKU
from .serializers import SKUSerializer
from mall.utils.pagination import StandardResultsSetPagination


# /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    '''商品列表数据查询'''

    # 指定过滤器:需要指定排序后端
    filter_backends = (OrderingFilter,)  # 一定要是可迭代的对象,可以使用列表
    # 指定排序字段：搭配filter_backends使⽤s的
    ordering_fields = ('create_time', 'price', 'sales') #可以使用列表

    # 指定序列化器
    serializer_class = SKUSerializer

    # pagination_class = StandardResultsSetPagination  # 局部配置


    # 指定查询集:因为要展示的商品列表需要明确的指定分类，所以重写获取查询集⽅法
    # queryset = SKU.objects.filter()

    def get_queryset(self):
        '''
        如果当前在视图中没有定义get/post方法,那么就没法定义一个参数用来接收正则组提取出来的url路径参数,
        可以利用args 或 kwargs属性取获取
        :return:
        '''
        print('self---------------->',self)
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(is_launched=True,category_id=category_id)

