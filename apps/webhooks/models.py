from django.db import models
from apps.stores.models import Store

# Create your models here.

class WebhookLog(models.Model):
    WEBHOOK_TYPE_CHOICES = [
        ('order_create', 'Order Create'),
        ('email', 'Email'),
        # Add more types as needed
    ]
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    webhook_type = models.CharField(max_length=50, choices=WEBHOOK_TYPE_CHOICES)
    status = models.CharField(max_length=50)
    payload = models.JSONField(null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.webhook_type} - {self.status} - {self.created_at}"
