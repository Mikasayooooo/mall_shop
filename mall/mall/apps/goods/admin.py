from django.contrib import admin

from . import models
from celery_tasks.html.tasks import generate_static_list_search_html


# 修改的是商品类别表里的数据
# 模型站点管理类不仅可以 设置admin界面的样式,还可以监听admin界面的事件
class GoodsCategoryAdmin(admin.ModelAdmin):
    '''商品类别模型站点管理类'''
    def save_model(self, request, obj, form, change):
        '''
        当点击admin的保存按钮时会调用此方法
        :param request: 保存时本次的请求对象
        :param obj: 本次要保存的模型对象
        :param form: admin中表单
        :param change: 是否改为
        :return:
        '''

        obj.save()

        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()
        # 先生成静态页面,后修改数据的话,永远慢一步, 必须先改数据,后生成

        # 需要使用celery
        # import time
        # time.sleep(5)

    def delete_model(self, request, obj):
        '''
        当点击admin的删除按钮时会调用此方法
        :param request: 保存时本次的请求对象
        :param obj: 本次要保存的模型对象
        :return:
        '''

        obj.delete()

        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()
        # 先生成静态页面,后修改数据的话,永远慢一步, 必须先改数据,后生成



# 如果 商品频道里的数据 改了,也需要重新生成
class GoodsChannelAdmin(admin.ModelAdmin):
    '''商品类别模型站点管理类'''
    def save_model(self, request, obj, form, change):

        obj.save()

        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()


    def delete_model(self, request, obj):

        obj.delete()

        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()



admin.site.register(models.GoodsCategory,GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel,GoodsChannelAdmin)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
