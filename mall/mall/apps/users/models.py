from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from django.conf import settings


# Create your models here.
from mall.utils.models import BaseModel


class User(AbstractUser):
    '''自定义用户模型类'''
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    # 模型已经建表,表中已经有数据,后追加的字段必须 要么 有默认值,要么 允许为空,否则就会报错
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,on_delete=models.SET_NULL, verbose_name='默认地址')
    # 一个默认地址对应一个用户

    class Meta:  # 配置数据库表名，及设置模型在admin站点显示的中文名
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_email_verify_url(self):
        '''生成邮箱激活链接'''
        # 1.创建加密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600 * 24)

        # 2.调用dumps方法进行加密,bytes类型
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()  # bytes--->string

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
            data = serializer.loads(token)  # token可能过期
        except BadData:
            return None
        else:
            id = data.get('user_id')  # 取字典使用get
            email = data.get('email')

            try:
                user = User.objects.get(id=id, email=email)
            except User.DoesNotExist:  # user 可能不存在
                return None
            else:
                return user


class Address(BaseModel):
    """
    ⽤户地址
    """
    # 多个地址对应一个用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='⽤户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货⼈')

    # areas.Area 应用名.模型名 ,在dev设置里的 用户认证出现过
    # 两种写法,还有一种,直接导入模型类,Area
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses',verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses',verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='⼿机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电⼦邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')


    class Meta:
        db_table = 'tb_address'
        verbose_name = '⽤户地址'
        verbose_name_plural = verbose_name
        # 按照修改的时间降序显示
        ordering = ['-update_time']
