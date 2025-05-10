from django.db import models
from apps.stores.models import Store

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    shopify_product_id = models.BigIntegerField()
    shopify_variant_id = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    is_digital = models.BooleanField(default=True)
    max_downloads_per_link = models.IntegerField(default=5)
    link_expiration_hours = models.IntegerField(default=72)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'shopify_product_id', 'shopify_variant_id')

    def __str__(self):
        return self.name

class File(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=1024)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    file_size_bytes = models.BigIntegerField()
    display_name = models.CharField(max_length=255, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.file_name

class LicenseKey(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    is_assigned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key
