from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.orders.models import DownloadLink, OrderItem
from apps.products.models import File
from django.utils import timezone

# Create your views here.

class CustomerDownloadView(APIView):
    permission_classes = []  # Public endpoint

    def get(self, request, uuid):
        try:
            link = DownloadLink.objects.get(uuid=uuid)
        except DownloadLink.DoesNotExist:
            return Response({'detail': 'Invalid or expired link.'}, status=status.HTTP_404_NOT_FOUND)
        if link.expires_at < timezone.now():
            return Response({'detail': 'This download link has expired.'}, status=status.HTTP_410_GONE)
        # Check download count limit (optional, if you want to enforce)
        product = link.order_item.product
        max_downloads = getattr(product, 'max_downloads_per_link', 5)
        if link.download_count >= max_downloads:
            return Response({'detail': 'Download limit reached.'}, status=status.HTTP_403_FORBIDDEN)
        # Get files for the product
        files = File.objects.filter(product=product)
        # For demo, return file names and fake URLs
        file_list = [
            {
                'file_name': f.file_name,
                'display_name': f.display_name or f.file_name,
                'download_url': f'https://fake-cdn.com/{f.file_path}?token=stub'
            }
            for f in files
        ]
        # Optionally increment download count
        link.download_count += 1
        link.save()
        return Response({'files': file_list, 'expires_at': link.expires_at}, status=status.HTTP_200_OK)
