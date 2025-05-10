from django.core.management.base import BaseCommand
from apps.stores.models import Store
from apps.products.models import Product
import requests

class Command(BaseCommand):
    help = 'Import up to 10 products (all variants) from Shopify into the Product table.'

    def handle(self, *args, **options):
        store = Store.objects.first()
        if not store:
            self.stdout.write(self.style.ERROR('No store found.'))
            return
        domain = store.shopify_domain
        token = store.shopify_access_token
        url = f'https://{domain}/admin/api/2023-10/products.json?limit=10'
        headers = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
        }
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed to fetch products: {resp.text}'))
            return
        products = resp.json().get('products', [])
        imported = 0
        for product in products:
            shopify_product_id = product['id']
            name = product['title']
            for variant in product.get('variants', []):
                shopify_variant_id = variant['id']
                # Skip if already exists
                if Product.objects.filter(shopify_product_id=shopify_product_id, shopify_variant_id=shopify_variant_id, store=store).exists():
                    continue
                Product.objects.create(
                    store=store,
                    shopify_product_id=shopify_product_id,
                    shopify_variant_id=shopify_variant_id,
                    name=name,
                )
                imported += 1
                if imported >= 10:
                    break
            if imported >= 10:
                break
        self.stdout.write(self.style.SUCCESS(f'Imported {imported} products/variants.')) 