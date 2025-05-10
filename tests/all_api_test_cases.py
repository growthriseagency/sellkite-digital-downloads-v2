import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from django.urls import reverse
from apps.stores.models import Store
from apps.plans.models import Plan
from apps.products.models import Product
from apps.products.models import File, LicenseKey
from apps.orders.models import Order, OrderItem, DownloadLink, AssignedLicenseKey
from apps.webhooks.models import WebhookLog
import json

client = APIClient()

# Helper to print test results
def print_result(name, resp):
    status = resp.status_code
    is_pass = 200 <= status < 300
    result = 'PASS' if is_pass else 'FAIL'
    print(f"{name}: {status} [{result}]")
    try:
        data = resp.json()
        print(json.dumps(data, indent=2))
    except Exception:
        content = resp.content.decode() if hasattr(resp.content, 'decode') else str(resp.content)
        if '<html' in content.lower():
            print('(HTML response, likely an error page)')
        else:
            print(content)
    print('-' * 60)

# 1. Plans
resp = client.get('/api/v1/plans/')
print_result('GET /api/v1/plans/', resp)

# 2. Store
resp = client.get('/api/v1/stores/me/')
print_result('GET /api/v1/stores/me/', resp)

# 3. Subscription
resp = client.get('/api/v1/stores/me/subscription/')
print_result('GET /api/v1/stores/me/subscription/', resp)

# 4. Products (list, create, retrieve, update, delete)
resp = client.get('/api/v1/products/')
print_result('GET /api/v1/products/', resp)

# Create a product (simulate minimal required fields)
store = Store.objects.first()
plan = store.current_plan if store else None
if store and plan and (plan.max_products is None or store.current_product_count < plan.max_products):
    data = {
        'shopify_product_id': 999999,
        'shopify_variant_id': 888888,
        'name': 'Test Product',
        'is_digital': True,
        'max_downloads_per_link': 5,
        'link_expiration_hours': 72,
    }
    resp = client.post('/api/v1/products/', data, format='json')
    print_result('POST /api/v1/products/', resp)
    product_id = resp.json().get('id') if resp.status_code in (200, 201) else None
else:
    product_id = None

if product_id:
    resp = client.get(f'/api/v1/products/{product_id}/')
    print_result('GET /api/v1/products/{id}/', resp)
    data = {'name': 'Test Product Updated'}
    resp = client.put(f'/api/v1/products/{product_id}/', data, format='json')
    print_result('PUT /api/v1/products/{id}/', resp)
    resp = client.delete(f'/api/v1/products/{product_id}/')
    print_result('DELETE /api/v1/products/{id}/', resp)

# 5. Files (list, create, delete)
product = Product.objects.first()
if product:
    resp = client.get(f'/api/v1/products/{product.id}/files/')
    print_result('GET /api/v1/products/{id}/files/', resp)
    data = {
        'file_name': 'test.txt',
        'file_path': 'https://fake-url.com/test.txt',
        'file_size_bytes': 1234,
    }
    resp = client.post(f'/api/v1/products/{product.id}/files/', data, format='json')
    print_result('POST /api/v1/products/{id}/files/', resp)
    file_id = resp.json().get('id') if resp.status_code in (200, 201) else None
    if file_id:
        resp = client.delete(f'/api/v1/products/{product.id}/files/{file_id}/')
        print_result('DELETE /api/v1/products/{id}/files/{file_id}/', resp)

# 6. License Keys (list, create, delete)
if product:
    resp = client.get(f'/api/v1/products/{product.id}/license-keys/')
    print_result('GET /api/v1/products/{id}/license-keys/', resp)
    data = {'key': 'TEST-KEY-123'}
    resp = client.post(f'/api/v1/products/{product.id}/license-keys/', data, format='json')
    print_result('POST /api/v1/products/{id}/license-keys/', resp)
    key_id = resp.json().get('id') if resp.status_code in (200, 201) else None
    if key_id:
        resp = client.delete(f'/api/v1/products/{product.id}/license-keys/{key_id}/')
        print_result('DELETE /api/v1/products/{id}/license-keys/{key_id}/', resp)

# 7. Webhook (order create)
if store:
    payload = {
        'id': 123456789,
        'email': 'customer@example.com',
        'line_items': [
            {
                'product_id': product.shopify_product_id if product else 1,
                'variant_id': product.shopify_variant_id if product else 1,
                'quantity': 1,
            }
        ],
    }
    headers = {'X-Shopify-Shop-Domain': store.shopify_domain}
    resp = client.post('/api/v1/webhooks/shopify/orders/create/', payload, format='json', **{'HTTP_X_SHOPIFY_SHOP_DOMAIN': store.shopify_domain})
    print_result('POST /api/v1/webhooks/shopify/orders/create/', resp) 