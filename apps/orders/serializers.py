from rest_framework import serializers
from .models import Order, OrderItem, DownloadLink, AssignedLicenseKey

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class DownloadLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadLink
        fields = '__all__'

class AssignedLicenseKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedLicenseKey
        fields = '__all__' 