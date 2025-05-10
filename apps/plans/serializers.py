from rest_framework import serializers
from .models import Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id',
            'name',
            'price_monthly',
            'price_annually',
            'max_products',
            'max_orders_per_month',
            'max_storage_gb',
            'allow_custom_email_template',
        ] 