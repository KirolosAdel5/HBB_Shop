from django.contrib import admin
from .models import Cart, Cartitems

class CartitemsInline(admin.TabularInline):
    model = Cartitems

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartitemsInline]
    
    list_display = ('id', 'user', 'created',)  # Add fields you want to display

    search_fields = ('user__username',)  # Add fields you want to search by
