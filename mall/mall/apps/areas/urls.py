from django.conf.urls import url
# DefaultRouter
# SimpleRouter 不会给你多带一个根路由
from rest_framework.routers import DefaultRouter


from . import views

urlpatterns = [
    # 查询所有省
    # url(r'^areas/$', views.AreaListView.as_view()),
    # # 查询单一省或市
    # url(r'^areas/(?P<pk>\d+)/$', views.AreaDetailView.as_view()),
]


# 视图集的路由处理
router = DefaultRouter()
# 不指定 base_name,会去找 queryset后面的模型,我这里没有定义queryset,所以必须写
# 查找 /areas
router.register(r'areas',views.AreaViewSet,base_name='area')
urlpatterns += router.urls