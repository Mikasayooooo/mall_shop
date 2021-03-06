import xadmin


from . import models
from xadmin import views



class SKUAdmin(object):
    '''SKU的模型站点管理类'''

    model_icon = 'fa fa-gift'  # 图标
    list_display = ['id', 'name', 'price', 'stock', 'sales', 'comments']  # 默认显示字段



xadmin.site.register(models.GoodsCategory)
xadmin.site.register(models.GoodsChannel)
xadmin.site.register(models.Goods)
xadmin.site.register(models.Brand)
xadmin.site.register(models.GoodsSpecification)
xadmin.site.register(models.SpecificationOption)
xadmin.site.register(models.SKU,SKUAdmin)
xadmin.site.register(models.SKUSpecification)
xadmin.site.register(models.SKUImage)




class BaseSetting(object):
    """xadmin的基本配置"""

    enable_themes = True # 开启主题切换功能
    use_bootswatch = True # 可以使用更多主题

xadmin.site.register(views.BaseAdminView, BaseSetting)


class GlobalSettings(object):
    """xadmin的全局配置"""

    site_title = "美多商城运营管理系统" # 设置站点标题
    site_footer = "美多商城集团有限公司" # 设置站点的⻚脚
    menu_style = "accordion" # 设置菜单折叠

xadmin.site.register(views.CommAdminView, GlobalSettings)