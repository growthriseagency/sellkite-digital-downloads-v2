from django.db import models
from apps.stores.models import Store
from apps.products.models import Product, LicenseKey

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    shopify_order_id = models.BigIntegerField()
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.shopify_order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order_id}"

class DownloadLink(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    uuid = models.UUIDField(unique=True)
    url = models.CharField(max_length=1024)
    expires_at = models.DateTimeField()
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.uuid)

class AssignedLicenseKey(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    license_key = models.ForeignKey(LicenseKey, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assigned {self.license_key_id} to OrderItem {self.order_item_id}"
