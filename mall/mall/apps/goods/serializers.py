from rest_framework import serializers


from .models import SKU



class SKUSerializer(serializers.ModelSerializer):
    '''sku商品序列化器'''

    class Meta:
        model = SKU
        fields = ['id','name','price','comments','default_image_url']