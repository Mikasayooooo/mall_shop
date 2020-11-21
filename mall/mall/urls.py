"""mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 这里的 路由地址不能改 ckeditor/,因为这是 admin站点访问的路径
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),  # 富文本编辑

    url(r'^', include('verifications.urls')),  # 发送短信模块

    url(r'^', include('users.urls')),  # 用户模块

    url(r'^oauth/', include('oauth.urls')),  # QQ模块
    # 不要在主路由后面加$,不然子路由匹配不到

    url(r'^', include('areas.urls')),  # 省市区模块
]
