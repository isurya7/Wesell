from django.contrib import admin
from .models import Product, Customer, WishlistItem, Order, CartItem, Payment

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'selling_price', 'discount_price', 'description', 'category', 'product_image']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'locality', 'city', 'mobile', 'zipcode', 'state']

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'size', 'added_at', 'get_total_price']

    def get_total_price(self, obj):
        return obj.get_item_price()
    
    get_total_price.short_description = 'Total Price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'size', 'get_total_price']

    def get_total_price(self, obj):
        return obj.total_price()
    
    get_total_price.short_description = 'Total Price'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'product', 'size', 'quantity', 'user', 'number', 
        'address', 'pincode', 'state', 'total_amount', 'mode_of_payment', 'added_at', 'order_state'
    ]
    list_editable = ['order_state']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user', 'product')
        return queryset

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'razorpay_order_id', 'razorpay_payment_status', 'razorpay_payment_id', 'paid')
    search_fields = ['user__username', 'razorpay_order_id', 'razorpay_payment_status', 'razorpay_payment_id']
