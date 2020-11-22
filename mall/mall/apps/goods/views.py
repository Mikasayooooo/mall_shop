from django.shortcuts import render
from rest_framework.generics import ListAPIView


from .models import SKU
from .serializers import SKUSerializer



class SKUListView(ListAPIView):
    '''商品列表数据查询'''


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

    serializer_class = SKUSerializer