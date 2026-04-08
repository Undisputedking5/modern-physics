from django.contrib import admin
from .models import Order, OrderItem, MpesaTransaction, MpesaConfiguration

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('resource', 'title', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'total_amount', 'created_at', 'updated_at')

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('checkout_request_id', 'phone_number', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('merchant_request_id', 'checkout_request_id', 'phone_number')
    readonly_fields = ('order', 'merchant_request_id', 'checkout_request_id', 'amount', 'phone_number', 'mpesa_receipt_number', 'result_code', 'result_desc', 'status', 'created_at')

@admin.register(MpesaConfiguration)
class MpesaConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_code', 'is_sandbox')
