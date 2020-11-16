from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    # 注册用户
    url(r'^users/$', views.UserView.as_view()),
    # 判断用户名是否已经注册
    url(r'^username/(?P<username>\w{5,20})/count/$', views.UsernameView.as_view()),
    # 判断手机号是否已经注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # JWT登录
    url(r'^authorizations/$', obtain_jwt_token),   # 仅仅生成token,认证是属于django的,只是封装了一下
    #     obtain_jwt_token = ObtainJSONWebToken.as_view()
]
