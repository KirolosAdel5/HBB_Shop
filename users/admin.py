from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address

class AddressInline(admin.StackedInline):  # You can also use admin.TabularInline for a more compact display
    model = Address
    extra = 1  # Number of empty forms to display

class CustomUserAdmin(UserAdmin):
    inlines = [AddressInline]  # Include the AddressInline inlines

    list_display = ('id', 'username', 'phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'phone_number', 'first_name', 'last_name')

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'city', 'full_name', 'phone', 'address_type', 'created_at', 'updated_at')
    search_fields = ('customer__username', 'customer__phone_number', 'city', 'full_name', 'phone')
