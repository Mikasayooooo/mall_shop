from rest_framework import serializers
import re
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from .models import User,Address
from celery_tasks.email.tasks import send_verify_email


class CreateUserSerializer(serializers.ModelSerializer):
    '''注册序列化器'''

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)  # 临时定义一个字段

    class Meta:
        model = User  # 从User模型中映射序列化器字段
        # fields = '__all__'                               模型临时加一个token属性,token别忘加
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validated_mobile(self, value):
        '''单独校验手机号'''
        print('value------------->', value)

        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式有误')
        return value

    def validated_allow(self, value):
        '''是否同意协议'''
        print('value------------->', value)

        # 因为前端为 true,后端为True,所以要校验 是否为true
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        '''校验密码两个是否相同'''
        print('attrs------------->', attrs)

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 校验验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)

        # 向 redis存储数据时都是以字符串进行存储的,取出来后都是bytes类型[bytes]

        # 首先判断 redis里存的验证码是否过期,再判断 两个验证码是否相等,先后顺序注意!!!
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            # 注意这里 从redis中取出数据里需要进行解码操作
            raise serializers.ValidationError('验证码错误')
        return attrs

    def create(self, validated_data):
        print('validated_data------------->', validated_data)

        # 把不需要存储的 password2,sms_code,allow 从字段中移除
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 把密码先取出来
        password = validated_data.pop('password')

        # 创建用户模型对象,给模型中的username和mobile属性赋值
        #  **validated_data 解压成 键值队形式,如 name='lhl'
        #  *data 是解压 元祖和列表
        user = User(**validated_data)

        # 把密码加密后再赋值给user的password属性
        user.set_password(password)

        # 保存到数据库
        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用,生成jwt

        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt

        user.token = token  # 这里的token必须和上面序列化器中定义的一致

        return user  # 在进行序列化的那一刻,就会多增加 token


# 序列化字段在 模型类中有,只需要通过ModelSerializer映射过来就行
# 只需要序列化-->json(给前端),所以不需要关注类型,选项,校验等
class UserDetailSerializer(serializers.ModelSerializer):
    '''用户详细序列化器'''

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'eamil_active']


class EmailSerializer(serializers.ModelSerializer):
    '''更新邮箱序列化器'''

    class Meta:
        model = User
        fields = ['id', 'email']  # 这里的邮箱允许为空,不符合我们的要求
        # email = models.EmailField(_('email address'), blank=True)
        extra_kwargs = {
            'email': {
                'required': True  # 不允许为空,
            }
        }

    def update(self, instance, validated_data):
        '''此方法重写目的不是为了修改,而是借用此时机 发送激活邮箱'''

        print('instance--------->', instance)
        print('validated_data---------->', validated_data)
        instance.email = validated_data.get('email')
        instance.save()
        print('instance--------->', type(instance))
        '''
        instance---------> liuhaoli
        validated_data----------> {'email': '1056205431@qq.com'}
        instance---------> <class 'users.models.User'>
        '''

        # 将来需要在此继续写发邮箱的功能
        # 异步发邮件

        # ⽣成激活链接
        # token 后面需要传用户对象,user,直接在模型中定义,self即用户对象
        # http://www.meiduo.site:8080/success_verify_email.html?token=1'
        # verify_url = '使⽤itsdangerous⽣成激活链接'
        verify_url = instance.generate_email_verify_url()

        send_verify_email.delay(instance.email, verify_url=verify_url)

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """⽤户地址序列化器"""

    # 这里的province,city,district已经有了还要重新定义
    # 因为 着三个字段是外键,映射过来默认是PrimaryKeyRelatedField,只能得到id
    # 这里需要改变他们的类型,所有需要自己重新定义
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """验证⼿机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('⼿机号格式错误')
        return value

    def create(self, validated_data):
        user = self.context['request'].user # 获取用户模型对象
        validated_data['user'] = user  #将用户模型保存到字典中
        return Address.objects.create(**validated_data)
