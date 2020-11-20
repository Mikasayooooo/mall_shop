from rest_framework import serializers
from .models import Area



class AreaSerializer(serializers.ModelSerializer):
    '''省的 序列化器'''

    class Meta:
        model = Area
        fields = ['id','name']


