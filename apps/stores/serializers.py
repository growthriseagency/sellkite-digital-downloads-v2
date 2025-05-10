from rest_framework import serializers
from .models import Store
from apps.plans.serializers import PlanSerializer

class StoreSubscriptionSerializer(serializers.ModelSerializer):
    current_plan = PlanSerializer(read_only=True)

    class Meta:
        model = Store
        fields = [
            'current_plan',
            'subscription_id_external',
            'subscription_status',
            'current_billing_period_ends',
            'current_product_count',
            'current_storage_used_bytes',
            'current_month_order_count',
            'last_order_count_reset_at',
        ]

class StoreRetrieveSerializer(serializers.ModelSerializer):
    current_plan = PlanSerializer(read_only=True)

    class Meta:
        model = Store
        fields = [
            'shopify_domain',
            'email',
            'is_active',
            'current_plan',
            'created_at',
            'updated_at',
        ] 