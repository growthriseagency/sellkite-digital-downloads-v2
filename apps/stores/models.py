from django.db import models
from apps.plans.models import Plan

class Store(models.Model):
    shopify_domain = models.CharField(max_length=255, unique=True)
    shopify_access_token = models.CharField(max_length=255)  # Should be encrypted in production
    email = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    current_plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    subscription_id_external = models.CharField(max_length=255, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, blank=True, null=True)
    current_billing_period_ends = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_product_count = models.IntegerField(default=0)
    current_storage_used_bytes = models.BigIntegerField(default=0)
    current_month_order_count = models.IntegerField(default=0)
    last_order_count_reset_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.shopify_domain
