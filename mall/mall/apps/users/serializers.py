from rest_framework import serializers

from . models import User

import re
from django_redis import get_redis_connection

from rest_framework_jwt.settings import api_settings


class CreateUserSerializer(serializers.ModelSerializer):
    '''注册序列化器'''


    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='token',read_only=True)  # 临时定义一个字段

    class Meta:
        model = User  # 从User模型中映射序列化器字段
        # fields = '__all__'                               模型临时加一个token属性,token别忘加
        fields = ['id','username','password','password2','mobile','sms_code','allow','token']
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


    def validated_mobile(self,value):
        '''单独校验手机号'''
        print('value------------->',value)

        if not re.match(r'1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机格式有误')
        return value


    def validated_allow(self,value):
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

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER #引用jwt中的叫jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER #函数引用,生成jwt

        payload = jwt_payload_handler(user) #根据user生成用户相关的载荷
        token = jwt_encode_handler(payload) #传入载荷生成完整的jwt

        user.token = token  # 这里的token必须和上面序列化器中定义的一致

        return user  # 在进行序列化的那一刻,就会多增加 token

