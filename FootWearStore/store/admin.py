from django.contrib import admin
from . import models
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'size')
    list_filter = ('size', 'price')
    prepopulated_fields = {'slug': ('name', ),}

admin.site.register(models.Product, ProductAdmin)