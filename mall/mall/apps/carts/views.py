from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response




class CartView(APIView):
    '''购物车增删改查'''

    def perform_authentication(self, request):
        '''重写此方法,直接pass,可以延后认证,延后到第一次通过 request.user或request.auth才去认证'''
        pass

    def post(self,request):
        '''新增'''

        try:
            # 执行此代码时会执行认证逻辑,如果登录用户认证成功没有异常,但是未登录用户认证会报异常
            user = request.user
        except:
            user = None


    def get(self,request):
        '''查询'''
        pass

    def put(self,request):
        '''修改'''
        pass

    def delete(self,request):
        '''删除'''
        pass
