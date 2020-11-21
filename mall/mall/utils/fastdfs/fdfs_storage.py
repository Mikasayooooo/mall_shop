from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

from django.conf import settings

class FastDFSStorage(Storage):
    '''自定义文件系统存储类'''

    # 这里必须设置 None,因为 Django必须能够不带任何参数来实例化你的存储类
    def __init__(self,client_path=None,base_url=None):

        # 使用面向对象的思想
        self.client_path = client_path or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_BASE_URL

        # 这样写太麻烦
        # if client_path:
        #     self.client_path = client_path
        # else:
        #     self.client_path = settings.FDFS_CLIENT_CONF


    def _open(self, name, mode='rb'):
        '''
        存储类⽤于打开⽂件: 因为必须实现,但是此处是⽂件存储不需要打开⽂件,所以重写之后什么也不做pass
        :param name: # 要打开的⽂件的名字
        :param mode: # 打开模式,read bytes]
        :return: None
        '''
        pass

    def _save(self, name, content):
        '''
        实现⽂件存储: 在这个⽅法⾥⾯将⽂件转存到FastDFS服务器
        :param name: 要存储的⽂件名字
        :param content: 要存储的⽂件对象, File类型的对象,将来使⽤content.read()读取对象中的⽂件⼆进制
        :return: file_id
        '''

        # 1.创建fastDFS客户端
        # client = Fdfs_client('mall/utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.client_path)

        # 2.通过客户端调用上传的方法上传文件到fastDFS服务器
        # client.upload_by_filename('要上传文件的绝对路径') 只能通过文件绝对路径进行上传,
        # 此方式上传的文件会有后缀
        # upload_by_buffer 可以通过文件二进制数据进行上传, 上传后的文件没有后缀
        ret = client.upload_by_buffer(content.read())

        # 3.判断文件是否上传成功
        if ret.get('Status') != 'Upload successed.':
            raise Exception('Upload file failed.')

        # 4.获取file_id
        file_id = ret.get('Remote file_id')

        # 4.返回file_id
        return file_id

    def exists(self, name):
        '''
        当要进行上传时都调用此方法判断文件是否已经上传,如果没有上传才会调用save方法进行上传
        :param name: 要上传的文件名
        :return: True(表示文件已存在,不需要上传),Fasle(文件不存在,需要上传)
        '''
        return False

    def url(self, name):
        '''
        当要访问图片时,就会调用此方法获取图片文件的绝对路径
        :param name: 要访问图片的file_id
        :return: 完整的图片访问路径: storage_server IP:8888 + file_id
        '''
        # return 'http://192.168.36.130:8888/' + name
        # return settings.FDFS_BASE_URL + name
        return self.base_url + name

