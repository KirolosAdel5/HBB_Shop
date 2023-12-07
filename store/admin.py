from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    ProductSpecificationValue,
    ProductType,
    Tag,
    CategoryImage,
    Review
)


class ProductSpecification(admin.TabularInline):
    model = ProductSpecification
    
@admin.register(ProductType)
class Admin(admin.ModelAdmin):
    inlines = [
        ProductSpecification 
    ]
    list_display  = ('name','is_active','get_product_count','related_specifications','actions_column')
    
    def get_product_count(self, obj):
        return Product.objects.filter(product_type=obj).count()

    get_product_count.short_description = 'Number of Products'
    
    def actions_column(self, obj):
        edit_url = reverse('admin:store_producttype_change', args=[obj.id])
        delete_url = reverse('admin:store_producttype_change', args=[obj.id])

        edit_icon = format_html('<a href="{}"><i class="fas fa-edit"></i></a>', edit_url)
        delete_icon = format_html('<a href="{}" onclick="return confirm(\'Are you sure?\')"><i class="fas fa-trash-alt"  style="color: red;"></i></a>', delete_url)

        return format_html('{} {}', edit_icon, delete_icon)

    actions_column.short_description = 'Actions'
    actions_column.allow_tags = True

    def related_specifications(self, obj):
        specifications = obj.productspecification_set.all()
        if not specifications:
            return
        output = []
        for specification in specifications:
            output.append(f"{specification.name}")
        return ', '.join(output)        
        
    related_specifications.short_description = "Related Specifications"



class ProductImageInline(admin.TabularInline):
    model = ProductImage

class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
class CustomMPTTModelAdmin(MPTTModelAdmin):
    inlines = [CategoryImageInline]
    list_display = ('name', 'parent_name', 'product_count','actions_column')
    list_filter = ('is_active', )
    search_fields = ('name', )

    def parent_name(self, obj):
        return obj.get_parent().name if obj.get_parent() else None

    parent_name.short_description = 'Parent Category'

    def product_count(self, obj):
        return obj.product_set.count()

    product_count.short_description = 'Number of Products'

    def actions_column(self, obj):
        edit_url = reverse('admin:store_category_change', args=[obj.id])
        delete_url = reverse('admin:store_category_delete', args=[obj.id])

        edit_icon = mark_safe(f'<a href="{edit_url}"><i class="fas fa-edit"></i></a>')
        delete_icon = mark_safe(f'<a href="{delete_url}" onclick="return confirm(\'Are you sure?\')"><i class="fas fa-trash-alt" style="color: red;"></i></a>')

        return mark_safe(f'{edit_icon} {delete_icon}')

    actions_column.short_description = 'Actions'


admin.site.register(Category, CustomMPTTModelAdmin)

class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue



class ProductTagsForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Tags', is_stacked=False),
        required=False  # Set required to False to make it not required

    )

    class Meta:
        model = Product
        fields = '__all__'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_product_count', 'related_products_names','actions_column')

    def get_product_count(self, obj):
        return Product.objects.filter(tags=obj).count()

    get_product_count.short_description = 'Number of Products'

    def related_products_names(self, obj):
        related_products = Product.objects.filter(tags=obj)
        return ', '.join([product.title for product in related_products])

    related_products_names.short_description = 'Related Products'

    def actions_column(self, obj):
        edit_url = reverse('admin:store_tag_change', args=[obj.id])
        delete_url = reverse('admin:store_tag_delete', args=[obj.id])

        edit_icon = format_html('<a href="{}"><i class="fas fa-edit"></i></a>', edit_url)
        delete_icon = format_html('<a href="{}" onclick="return confirm(\'Are you sure?\')"><i class="fas fa-trash-alt"  style="color: red;"></i></a>', delete_url)

        return format_html('{} {}', edit_icon, delete_icon)

    actions_column.short_description = 'Actions'
    actions_column.allow_tags = True


class ReviewInline(admin.TabularInline):
    model = Review  # Include the Review model


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','display_image', 'get_category_hierarchy', 'product_type', 'regular_price', 'discount_price', 'stock', 'user','get_tags','actions_column')

    # Optional: Add filters and search fields for better admin interface
    list_filter = ('category', 'product_type', 'is_active','user','tags')
    search_fields = ('title', 'description','user','tags')
    list_per_page = 20  # Set the number of items per page
    
    inlines = [
        ProductSpecificationValueInline,
        ProductImageInline,
        ReviewInline
    ]
    form = ProductTagsForm
    
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    
    get_tags.short_description = 'Tags'

    def get_category_hierarchy(self, obj):
        return ' > '.join([category.name for category in obj.category.get_ancestors(include_self=True)])
    
    get_category_hierarchy.short_description = 'Category Hierarchy'

    def display_image(self, obj):
        if obj.product_image.exists():
            image_url = obj.product_image.first().image.url
            return format_html(f'<img src="{image_url}" width="50" height="50" />')
        return None

    display_image.short_description = 'Product Image'
    
    def actions_column(self, obj):
        edit_url = reverse('admin:store_product_change', args=[obj.id])
        delete_url = reverse('admin:store_product_delete', args=[obj.id])

        edit_icon = format_html('<a href="{}"><i class="fas fa-edit"></i></a>', edit_url)
        delete_icon = format_html('<a href="{}" onclick="return confirm(\'Are you sure?\')"><i class="fas fa-trash-alt"  style="color: red;"></i></a>', delete_url)

        return format_html('{} {}', edit_icon, delete_icon)

    actions_column.short_description = 'Actions'
    actions_column.allow_tags = True
