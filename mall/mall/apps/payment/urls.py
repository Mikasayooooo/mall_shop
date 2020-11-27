from django.conf.urls import url

from . import views

urlpatterns = [
    # 获取支付宝支付url
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
]
