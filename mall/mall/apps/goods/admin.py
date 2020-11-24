from django.contrib import admin

from . import models
from celery_tasks.html.tasks import generate_static_list_search_html,generate_static_sku_detail_html


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
        '''

        :param request: 保存时本次的请求对象
        :param obj: 本次要保存的模型对象
        :param form: admin中表单
        :param change: 是否改为
        :return:
        '''

        obj.save()

        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()


    def delete_model(self, request, obj):

        obj.delete()

        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()



# @admin.register(models.SKU) 也可以通过装饰器的方式,这样 写了,下面就不需要写了
class SKUAdmin(admin.ModelAdmin):
    '''商品模型站点管理类'''
    def save_model(self, request, obj, form, change):
        '''

        :param request: 保存时本次的请求对象
        :param obj: 本次要保存的模型对象
        :param form: admin中表单
        :param change: 是否改为
        :return:
        '''

        obj.save()  # 千万不要少了这一行,不然admin的保存就无效

        # 重新生成新的列表静态界面
        generate_static_sku_detail_html.delay(obj.id)


    def delete_model(self, request, obj):

        obj.delete()

        # 重新生成新的列表静态界面
        generate_static_sku_detail_html.delay(obj.id)




class SKUImageAdmin(admin.ModelAdmin):
    '''商品图片模型站点管理类'''
    def save_model(self, request, obj, form, change):
        '''

        :param request: 保存时本次的请求对象
        :param obj: 本次要保存的模型对象
        :param form: admin中表单
        :param change: 是否改为
        :return:
        '''

        obj.save()  # 千万不要少了这一行,不然admin的保存就无效

        sku = obj.sku # 通过外键获取图片模型对象所关联的sku模型的id
        # 如果当前sku商品还没有默认图片,就给它设置一张默认图片
        if not sku.default_image_url:
            sku.default_image_url  = obj.image.url  # 获取图片路径

        # 重新生成新的列表静态界面
        generate_static_sku_detail_html.delay(sku.id)


    def delete_model(self, request, obj):

        obj.delete()

        sku = obj.sku   # 获取到图片模型对象关联的sku模型

        # 重新生成新的列表静态界面
        generate_static_sku_detail_html.delay(sku.id)






admin.site.register(models.GoodsCategory,GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel,GoodsChannelAdmin)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU,SKUAdmin)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage,SKUImageAdmin)
