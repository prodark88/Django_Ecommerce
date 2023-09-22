from django.contrib import admin
from .models import Order, OrderProduct, Payment

#@admin.register(OrderProduct)
@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    model = OrderProduct
    list_display = ('order', 'payment', 'user', 'product', 'quantity', 'product_price', 'ordered', 'created_at', 'updated_at')
    extra = 0
""" class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    list_display = ('order', 'payment', 'user', 'product', 'quantity', 'product_price', 'ordered', 'created_at', 'updated_at')
    extra = 0 """

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone', 'email')
    list_per_page = 20
    #inlines = [OrderProductInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_id', 'payment_method', 'amount_id', 'status')