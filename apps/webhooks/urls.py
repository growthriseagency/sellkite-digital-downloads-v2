from django.urls import path
from .views import ShopifyOrderCreateWebhook

urlpatterns = [
    path('api/v1/webhooks/shopify/orders/create/', ShopifyOrderCreateWebhook.as_view(), name='shopify-order-create-webhook'),
] 