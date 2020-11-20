from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView,ListAPIView,RetrieveAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin


from .models import Area
from .serializers import AreaSerializer,SubsSerializer


'''APIView'''
# class AreaListView(APIView):
#     '''查询所有省'''
#
#     def get(self,request):
#         # 1.获取指定的查询集,查询省
#         qs = Area.objects.filter(parent=None)
#
#         # 2.创建序列化器进行序列化
#         serializer = AreaSerializer(instance=qs,many=True)
#
#         # 3.响应
#         return Response(serializer.data)



'''GenericAPIView'''
# class AreaListView(GenericAPIView):
#     '''查询所有省'''
#
#     # 指定序列化器
#     serializer_class = AreaSerializer
#
#     # 获取指定的查询集
#     queryset = Area.objects.filter(parent=None)
#
#     def get(self,request):
#         # 1.获取指定的查询集,查询省
#         qs = self.get_queryset()
#
#         # 2.创建序列化器进行序列化
#         serializer = self.get_serializer(qs,many=True)
#
#         # 3.响应
#         return Response(serializer.data)




'''ListModelMixin'''
# class AreaListView(ListModelMixin,GenericAPIView):
#     '''查询所有省'''
#
#     # 指定序列化器
#     serializer_class = AreaSerializer
#
#     # 获取指定的查询集
#     queryset = Area.objects.filter(parent=None)
#
#     def get(self,request):
#         return self.list(request)




'''ListAPIView'''
# class AreaListView(ListAPIView):
#     '''查询所有省'''
#
#     # 指定序列化器
#     serializer_class = AreaSerializer
#
#     # 获取指定的查询集    这里只获取省
#     queryset = Area.objects.filter(parent=None)
#
#     # def get(self,request):
#     #     # 1.获取指定的查询集,查询省
#     #     # qs = Area.objects.filter(parent=None)
#     #     # qs = self.get_queryset()
#     #     #
#     #     # # 2.创建序列化器进行序列化
#     #     # # serializer = AreaSerializer(instance=qs,many=True)
#     #     # serializer = self.get_serializer(qs,many=True)
#     #     #
#     #     # # 3.响应
#     #     # return Response(serializer.data)
#     #
#     #     return self.list(request)


'''APIView'''
# class AreaDetailView(APIView):
#     '''查询单一的省或市'''
#
#     def get(self,request,pk):
#         # 1.根据pk查询出指定的省或市
#         try:
#             area = Area.objects.get(id=pk)
#         except Area.DoesNotExist:
#             return Response({'message':'无效pk'},status=status.HTTP_400_BAD_REQUEST)
#
#         # 2.创建序列化器进行序列化
#         serializer = SubsSerializer(instance=area)
#
#         # 3.响应
#         return Response(serializer.data)




'''RetrieveAPIView'''
# class AreaDetailView(RetrieveAPIView):
#     '''查询单一的省或市'''
#
#     # 指定序列化器
#     serializer_class = SubsSerializer
#
#     # 获取指定的查询集
#     queryset = Area.objects.all()
#
#     # def get(self,request,pk):
#     #     # 1.根据pk查询出指定的省或市
#     #     try:
#     #         area = Area.objects.get(id=pk)
#     #     except Area.DoesNotExist:
#     #         return Response({'message':'无效pk'},status=status.HTTP_400_BAD_REQUEST)
#     #
#     #     # 2.创建序列化器进行序列化
#     #     serializer = SubsSerializer(instance=area)
#     #
#     #     # 3.响应
#     #     return Response(serializer.data)



'''ReadOnlyModelViewSet'''
# 注意: CacheResponseMixin,ReadOnlyModelViewSet 顺序不能发生变化,会影响到继承链
# 放前面会优先调用 CacheResponseMixin 的父类 ListCacheResponseMixin 里的 list方法
class AreaViewSet(CacheResponseMixin,ReadOnlyModelViewSet):

    # 指定查询集(两种指定查询集的方式)
    # queryset =  只能指定一个查询集

    # 重写
    def get_queryset(self):
        print('AreaViewSet-------self---------->',self)
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    # 指定序列化器(两种指定序列化器的方式)
    # serializer_class =

    # 注意: 这里别写成get_serializer(self)
    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsSerializer