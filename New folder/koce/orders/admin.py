from django.contrib import admin
from .models import Category, Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'waiter', 'status', 'created_at')
    list_filter = ('status', 'waiter')
    inlines = [OrderItemInline]

admin.site.register(Category)
admin.site.register(Product)