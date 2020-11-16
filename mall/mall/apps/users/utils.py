from django.contrib.auth.backends import ModelBackend
import re
from .models import User

def jwt_response_payload_handler(token, user=None, request=None):
    '''重写JWT登录视图的构造响应数据函数,多追加user_id和username'''
    return {
        'token': token,
        'user_id':user.id,
        'username':user.username
    }



def get_user_by_account(account):
    '''
    通过传入的账号动态获取user 模型对象
    :param account: 可以是手机号,有可能是用户名
    :return: user 或 None
    '''

    try:
        if re.match(r'1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
            # 有一个问题,纯数字的用户名是手机号格式,被当做手机号来查询,结果查询不到
            # 解决:注册的用户名必须不能以数字开头就搞定了

            # 需求:使用邮箱也能登录,只要校验一下用户名的格式是否是邮箱的格式就行了,再拿email字段去查询用户就行了(一种思想)

            # get 查询不到会报错
    except User.DoesNotExist:
        return None   # 如果没有查询到返回None
    else:
        # 没报错就执行这句
        return user  # 注意不要写成模型类


class UsernameMobileAuthBackend(ModelBackend):
    '''修改Django的认证类,为了实现多账号登录'''

    def authenticate(self, request, username=None, password=None, **kwargs):

        # 获取 user
        user = get_user_by_account(username)

        # 判断当前前端传入的密码是否正确
        if user and user.check_password(password):

            # 返回user
            return user
