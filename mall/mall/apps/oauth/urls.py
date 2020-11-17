from django.conf.urls import url

from . import views

urlpatterns = [
    # 拼接QQ登录路由
    url(r'^qq/authorization/$', views.QQauthURLView.as_view()),
    # QQ登录后的回调
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),
]
