from django.contrib import admin
from .models import Product, File, LicenseKey

admin.site.register(Product)
admin.site.register(File)
admin.site.register(LicenseKey)
