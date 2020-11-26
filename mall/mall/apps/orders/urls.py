from django.conf.urls import url

from . import views

urlpatterns = [
    # 结算
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),
    # 保存订单
    url(r'^order/$', views.CommitOrderView.as_view()),
]
