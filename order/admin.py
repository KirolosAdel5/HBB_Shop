from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Order, OrderItem ,OrderStatus
from rest_framework.authtoken.models import TokenProxy

admin.site.unregister(TokenProxy)
admin.site.site_header = "HBB Admin Panel"
admin.site.site_title = "HBB Admin Panel"
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['product_info_link']

    def product_info_link(self, obj):
        if obj.product:
            product_url = reverse('admin:store_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', product_url, obj.product)
        return ''

    product_info_link.short_description = 'Product Info'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'address_link', 'payment_status', 'payment_mode',  'createAt','status_with_icon','order_price','status']
    list_filter = ['payment_status', 'status', 'createAt']
    search_fields = ['owner__username', 'createAt']
    inlines = [OrderItemInline]
    list_display_links = ['id', 'address_link' ]  # Make 'address_link' clickable
    list_per_page = 20  # Set the number of items per page
    list_editable = ['status']
    change_list_template = 'admin/order_analytics_list.html'
    def address_link(self, obj):
        if obj.address:
            address_url = reverse('admin:users_address_change', args=[obj.address.id])
            return format_html('<a href="{}">{}</a>', address_url, obj.address)
        return ''

    address_link.short_description = 'Address'
    
    def status_with_icon(self, obj):
        if obj.status == 'Delivered':
            return format_html('<span style="color: green;"><i class="fas fa-check"></i> Delivered</span>')
        elif obj.status == 'Processing':
            return format_html('<span style="color: orange;"><i class="fas fa-cogs"></i> Processing</span>')
        elif obj.status == 'Shipped':
            return format_html('<span style="color: blue;"><i class="fas fa-shipping-fast"></i> Shipped</span>')
        elif obj.status == 'Cancelled':
            return format_html('<span style="color: red;"><i class="fas fa-times"></i> Cancelled</span>')
        else:
            return obj.status

    status_with_icon.short_description = 'Status'
    status_with_icon.short_description = format_html('<i class="fas fa-info-circle"></i> Status')

    
    def order_price(self, obj):
        total_price = sum(item.product.regular_price * item.quantity for item in obj.orderitems.all() if item.product)
        return total_price

    order_price.short_description = 'Order Price'

  

admin.site.register(Order, OrderAdmin)
