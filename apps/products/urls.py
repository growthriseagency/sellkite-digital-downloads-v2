from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ProductViewSet, ProductFileViewSet, FileSignedUrlStubView, ProductLicenseKeyViewSet

router = DefaultRouter()
router.register(r'api/v1/products', ProductViewSet, basename='product')

urlpatterns = router.urls

# Nested file endpoints
urlpatterns += [
    path('api/v1/products/<int:product_id>/files/', ProductFileViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-file-list-create'),
    path('api/v1/products/<int:product_id>/files/<int:pk>/', ProductFileViewSet.as_view({'delete': 'destroy'}), name='product-file-delete'),
    path('api/v1/products/<int:product_id>/files/signed-url/', FileSignedUrlStubView.as_view(), name='product-file-signed-url'),
    path('api/v1/products/<int:product_id>/license-keys/', ProductLicenseKeyViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-licensekey-list-create'),
    path('api/v1/products/<int:product_id>/license-keys/<int:pk>/', ProductLicenseKeyViewSet.as_view({'delete': 'destroy'}), name='product-licensekey-delete'),
] 