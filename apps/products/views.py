from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, File, LicenseKey
from .serializers import ProductSerializer, FileSerializer, LicenseKeySerializer
from apps.stores.models import Store
from rest_framework.views import APIView

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        # For now, filter by the first store (simulate 'me')
        store = Store.objects.first()
        if not store:
            return Product.objects.none()
        return Product.objects.filter(store=store)

    def perform_create(self, serializer):
        store = Store.objects.first()
        if not store:
            raise Exception('Store not found.')
        plan = store.current_plan
        if plan and plan.max_products is not None and store.current_product_count >= plan.max_products:
            raise Exception('Product limit reached for your plan.')
        product = serializer.save(store=store)
        store.current_product_count += 1
        store.save()
        return product

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        store = instance.store
        response = super().destroy(request, *args, **kwargs)
        if store.current_product_count > 0:
            store.current_product_count -= 1
            store.save()
        return response

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

class ProductFileViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = FileSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return File.objects.filter(product_id=product_id)

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        store = Store.objects.first()  # Simulate 'me'
        plan = store.current_plan
        file_size = int(request.data.get('file_size_bytes', 0))
        storage_limit = plan.max_storage_gb * 1024 ** 3 if plan and plan.max_storage_gb else None
        warning = None
        if storage_limit and (store.current_storage_used_bytes + file_size > storage_limit):
            warning = 'Storage limit exceeded for your plan.'
        response = super().create(request, *args, **kwargs)
        store.current_storage_used_bytes += file_size
        store.save()
        if warning:
            response.data['warning'] = warning
        return response

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        serializer.save(product=product)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        store = Store.objects.first()  # Simulate 'me'
        file_size = instance.file_size_bytes
        response = super().destroy(request, *args, **kwargs)
        if store.current_storage_used_bytes >= file_size:
            store.current_storage_used_bytes -= file_size
            store.save()
        return response

class FileSignedUrlStubView(APIView):
    def post(self, request, product_id):
        # Stub: return a fake signed URL for now
        file_name = request.data.get('file_name')
        response = {
            'upload_url': f'https://fake-r2-url.com/{file_name}?signature=stub',
            'file_url': f'https://fake-r2-url.com/{file_name}'
        }
        return Response(response)

class ProductLicenseKeyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = LicenseKeySerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return LicenseKey.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        serializer.save(product=product)
