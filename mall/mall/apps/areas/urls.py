from django.conf.urls import url

from . import views

urlpatterns = [
    # 查询所有省
    url(r'^areas/$', views.AreaListView.as_view()),
]