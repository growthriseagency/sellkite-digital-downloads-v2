from django.urls import path
from .views import CustomerDownloadView

urlpatterns = [
    path('api/v1/download/<uuid:uuid>/', CustomerDownloadView.as_view(), name='customer-download'),
] 