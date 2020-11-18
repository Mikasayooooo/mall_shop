from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from django.conf import settings


# Create your models here.

class User(AbstractUser):
    '''自定义用户模型类'''
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    # 模型已经建表,表中已经有数据,后追加的字段必须 要么 有默认值,要么 允许为空,否则就会报错
    email_active = models.BooleanField(default=False,verbose_name='邮箱激活状态')

    class Meta:  # 配置数据库表名，及设置模型在admin站点显示的中文名
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


    def generate_email_verify_url(self):
        '''生成邮箱激活链接'''
        # 1.创建加密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY,3600*24)

        # 2.调用dumps方法进行加密,bytes类型
        data = {'user_id':self.id,'email':self.email}
        token = serializer.dumps(data).decode() # bytes--->string

        # 3.拼接激活url
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token


    # 这里使用静态方法,因为实例方法需要self,类方法需要cls,都不需要
    # 使用 类名.静态方法名 调用
    @staticmethod
    def check_verify_email_token(token):
        '''对token解密并查询对应的user'''

        # 1.创建加密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600 * 24)

        # 2.调用loads解密
        try:
            data = serializer.loads(token)      # token可能过期
        except BadData:
            return None
        else:
            id = data.get('user_id')   # 取字典使用get
            email = data.get('email')

            try:
                user = User.objects.get(id=id,email=email)
            except User.DoesNotExist:   # user 可能不存在
                return None
            else:
                return user