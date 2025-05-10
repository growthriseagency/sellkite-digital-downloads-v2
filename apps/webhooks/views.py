from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.stores.models import Store
from apps.products.models import Product, LicenseKey
from apps.orders.models import Order, OrderItem, DownloadLink, AssignedLicenseKey
from .models import WebhookLog
from django.utils import timezone
import uuid

# Create your views here.

class ShopifyOrderCreateWebhook(APIView):
    def post(self, request):
        payload = request.data
        # Find store by domain (Shopify sends X-Shopify-Shop-Domain header or in payload)
        shop_domain = request.headers.get('X-Shopify-Shop-Domain') or payload.get('shop_domain')
        store = Store.objects.filter(shopify_domain=shop_domain).first()
        if not store:
            WebhookLog.objects.create(
                store=None,
                webhook_type='order_create',
                status='error',
                payload=payload,
                message=f'Store not found for domain: {shop_domain}'
            )
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        plan = store.current_plan
        # Check plan order limit
        if plan and plan.max_orders_per_month is not None and store.current_month_order_count >= plan.max_orders_per_month:
            WebhookLog.objects.create(
                store=store,
                webhook_type='order_create',
                status='skipped',
                payload=payload,
                message='Plan order limit exceeded. Order not fulfilled.'
            )
            return Response({'detail': 'Plan order limit exceeded.'}, status=status.HTTP_403_FORBIDDEN)
        # Process order
        shopify_order_id = payload.get('id')
        email = payload.get('email')
        order = Order.objects.create(store=store, shopify_order_id=shopify_order_id, email=email)
        digital_fulfilled = False
        for item in payload.get('line_items', []):
            product = Product.objects.filter(store=store, shopify_product_id=item.get('product_id'), shopify_variant_id=item.get('variant_id')).first()
            if product and product.is_digital:
                order_item = OrderItem.objects.create(order=order, product=product, quantity=item.get('quantity', 1))
                # Create download link
                link_uuid = uuid.uuid4()
                DownloadLink.objects.create(
                    order_item=order_item,
                    uuid=link_uuid,
                    url=f'https://your-download-domain.com/download/{link_uuid}',
                    expires_at=timezone.now() + timezone.timedelta(hours=product.link_expiration_hours),
                )
                # Assign license key if available
                license_key = LicenseKey.objects.filter(product=product, is_assigned=False).first()
                if license_key:
                    AssignedLicenseKey.objects.create(order_item=order_item, license_key=license_key)
                    license_key.is_assigned = True
                    license_key.save()
                digital_fulfilled = True
        # Increment order count
        store.current_month_order_count += 1
        store.save()
        # Log fulfillment
        WebhookLog.objects.create(
            store=store,
            webhook_type='order_create',
            status='fulfilled' if digital_fulfilled else 'no_digital',
            payload=payload,
            message='Order processed and fulfilled.' if digital_fulfilled else 'Order processed, no digital items.'
        )
        # Log email action
        WebhookLog.objects.create(
            store=store,
            webhook_type='email',
            status='sent',
            payload={'order_id': order.id, 'email': email},
            message='Download email would be sent to customer.'
        )
        return Response({'detail': 'Order processed.'}, status=status.HTTP_200_OK)
