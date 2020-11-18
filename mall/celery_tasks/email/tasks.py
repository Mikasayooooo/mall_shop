from django.core.mail import send_mail

from celery_tasks.main import celery_app
from django.conf import settings


@celery_app.task(name='send_verify_email')
def send_verify_email(to_email,verify_url):

    '''
    发激活邮箱的邮件
    :param to_email: 收件人邮箱
    :param verify_url: 邮箱激活URL
    :return:
    '''

    subject = "mall商城邮箱验证"  # 邮件主题/标题
    html_message = '<p>尊敬的⽤户您好！</p>' \
                   '<p>感谢您使⽤mall商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    # def send_mail(subject:主题, message:普通邮件正文, from_email:发件人, recipient_list:收件人,列表[],
    #               fail_silently=False, auth_user=None, auth_password=None,
    #               connection=None, html_message=None:超文本的邮件内容):

    send_mail(subject,'',settings.EMAIL_FROM,[to_email],html_message=html_message)
    # 使用了配置文件的变量 settings.EMAIL_FROM,需要为celery使⽤django配置⽂件进⾏设置

