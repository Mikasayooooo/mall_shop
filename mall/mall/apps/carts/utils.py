import pickle,base64
from django_redis import get_redis_connection



def merge_cart_cookie_to_redis(request,user,response):
    '''
    登录时合并购物车
    :param request: 登录时借用过来的请求对象
    :param user: 登录时借用过来的用户对象
    :param response: 借用过来准备做删除cookie的响应对象
    :return:
    '''

    # 先获取cookie
    cart_str = request.COOKIES.get('cart')

    # 判断cookie中是否有购物车数据
    if not cart_str:
    # 如果cookie中没有购物车数据,直接返回
        return

    # 如果有,把cookie购物车中的字符串转换成字典
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 创建redis连接对象
    redis_conn = get_redis_connection('cart')

    # 创建redis管道对象
    pl = redis_conn.pipeline()

    # 遍历cookie大字典,把sku_id和count向redis中存储
    for sku_id in cart_dict:

        # 把cookie中的sku_id和count向redis中存储,如果存储的sku_id已经存在,则覆盖,不存在就是新增
        # 这里的user,必须是从 qq登录那传过来,request.user是 一个匿名用户
        pl.hset('cart_%d' % user.id,sku_id,cart_dict[sku_id]['count'])

        # 判断当前cookie中的商品是否勾选,如果勾选就把勾选的商品的sku_id存储到set集合中
        pl.sadd('selected_%d' % user.id,sku_id)

    # 执行管道
    pl.execute()

    # 删除cookie购物车数据
    response.delete_cookie('cart')
