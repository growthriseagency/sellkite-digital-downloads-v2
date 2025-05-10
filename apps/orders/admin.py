from django.contrib import admin
from .models import Order, OrderItem, DownloadLink, AssignedLicenseKey

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DownloadLink)
admin.site.register(AssignedLicenseKey)
