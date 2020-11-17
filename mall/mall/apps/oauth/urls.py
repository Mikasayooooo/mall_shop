from django.conf.urls import url

from . import views

urlpatterns = [
    # 拼接QQ登录路由
    url(r'^qq/authorization/$', views.QQauthURLView.as_view()),
]
