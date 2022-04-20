from django.contrib import admin
from . import models
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    list_filter = ('price',)
    prepopulated_fields = {'slug': ('name', ),}
    
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer)
admin.site.register(models.Cart)
admin.site.register(models.Size_Quantity)
admin.site.register(models.Feedback)