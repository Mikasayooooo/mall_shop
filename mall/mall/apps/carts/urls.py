from django.conf.urls import url

from . import views

urlpatterns = [
    # 购物车增删改查
    url(r'^carts/$', views.CartView.as_view()),
]
