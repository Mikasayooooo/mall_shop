from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User
from .utils import check_save_user_token


class QQAuthUserSerializer(serializers.Serializer):
    '''openid 绑定用户的序列化器'''
    # mobile password sms_code access_token
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号',regex=r'1[3-9]\d{9}$')
    password = serializers.CharField(label='密码',max_length=20,min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        # 1.把加密的openid取出来,解密
        access_token = attrs.pop('access_token')  # get有默认值,pop会将值弹出来,加密的access_token没用
        # access_token = attrs['access_token']  没找到会报错

        openid = check_save_user_token(access_token)

        if not openid:
            raise serializers.ValidationError('openid无效')

        # 1.1 把原本的openid重新添加到attrs字典(以备后期create方法中绑定使用)
        attrs['openid'] = openid

        # 2.校验验证码
        # 校验验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)

        # 向 redis存储数据时都是以字符串进行存储的,取出来后都是bytes类型[bytes]

        # 首先判断 redis里存的验证码是否过期,再判断 两个验证码是否相等,先后顺序注意!!!
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            # 注意这里 从redis中取出数据里需要进行解码操作
            raise serializers.ValidationError('验证码错误')

        # 3.拿手机号查询user表，并且密码正确，把当前的user对象存储到反序列化大字典中以备后期使用
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            else:
                # 如果用户已经存在并且密码正确,把当前的user对象存储到反序列化大字典中以备后期使用
                attrs['user'] = user

        return attrs


    def create(self, validated_data):
        pass
