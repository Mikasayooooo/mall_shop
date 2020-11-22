from celery import Celery

# 为celery使⽤django配置⽂件进⾏设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings.dev'


# 1.创建celery实例对象
celery_app = Celery('mall')

# 2.加载配置文件
celery_app.config_from_object('celery_tasks.config')

# 3.自动注册异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email','celery_tasks.html'])