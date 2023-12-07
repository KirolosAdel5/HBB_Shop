from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Avg

class Category(MPTTModel):
    """
    Category Table implimented with MPTT.
    """

    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )
    slug = models.SlugField(unique=True,verbose_name=_("Category safe URL"), max_length=255)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def get_absolute_url(self):
        return reverse("store:category_list", args=[self.slug])

    def __str__(self):
        return self.name
    def get_parent(self):
        try:
            # Assuming there's a ForeignKey field named 'parent' in your Category model
            return self.parent
        except Category.DoesNotExist:
            return None
    
    def get_all_categories_choices(self):
        """
        Get all categories and their descendants as choices.
        """
        categories = Category.objects.all()
        choices = [(category.slug, category.name) for category in categories.get_descendants(include_self=True)]
        return choices    
    def save(self, *args, **kwargs):
        # Check if the category is at level 0 and set the banner image accordingly
        if self.level == 0:
            self.banner_image = 'path_to_default_banner_image'  # Set the path to your default banner image
        else:
            self.banner_image = None

        super().save(*args, **kwargs)

class CategoryImage(models.Model):
    """
    The Category Image table.
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_images")
    image = models.ImageField(
        verbose_name=_("Image"),
        help_text=_("Upload a category image"),
        upload_to="images/category_images/",
        default="images/category_images/default.png",
    )
    alt_text = models.CharField(
        verbose_name=_("Alternative text"),
        help_text=_("Please add alternative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Category Image")
        verbose_name_plural = _("Category Images")

    def save(self, *args, **kwargs):
        # Set upload_to dynamically based on the category's slug
        self.image.upload_to = f"images/category_images/{self.category.slug}/"
        super().save(*args, **kwargs)
class ProductType(models.Model):
    """
    ProductType Table will provide a list of the different types
    of products that are for sale.
    """

    name = models.CharField(verbose_name=_("Product Name"), help_text=_("Required"), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name

class ProductSpecification(models.Model):
    """
    The Product Specification Table contains product
    specifiction or features for the product types.
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    name = models.CharField(verbose_name=_("Name"), help_text=_("Required"), max_length=255)

    class Meta:
        verbose_name = _("Product Specification")
        verbose_name_plural = _("Product Specifications")

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    The Product table contining all product items.
    """
    
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT,null=True)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    title = models.CharField(
        verbose_name=_("title"),
        help_text=_("Required"),
        max_length=255,
    )
    description = models.TextField(verbose_name=_("description"), help_text=_("Not Required"), blank=True)
    slug = models.SlugField(unique=True,max_length=255)
    regular_price = models.DecimalField(
        verbose_name=_("Regular price"),
        help_text=_("Maximum 999.99"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 999.99."),
            },
        },
        max_digits=5,
        decimal_places=2,
    )

    discount_price = models.DecimalField(
        verbose_name=_("Discount price"),
        help_text=_("Maximum 999.99"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 999.99."),
            },
        },
        max_digits=5,
        decimal_places=2,
        default=0.0  # Set a default value

    )
    
    brand = models.CharField(max_length=200,default="",blank=True)

    stock = models.PositiveIntegerField(
        verbose_name=_("Stock"),
        help_text=_("The available stock quantity"),
        default=0
    )
    rating = models.FloatField(
        verbose_name=_("Rating"),
        help_text=_("The average rating for the product"),
        blank=True,
        null=True,
        default=0,
    )
    
    is_active = models.BooleanField(
        verbose_name=_("Product visibility"),
        help_text=_("Change product visibility"),
        default=True,
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField('Tag', related_name='products', blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    def __str__(self):
        return self.title
    

class ProductSpecificationValue(models.Model):
    """
    The Product Specification Value table holds each of the
    products individual specification or bespoke features.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specification_values')
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(
        verbose_name=_("value"),
        help_text=_("Product specification value (maximum of 255 words"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Product Specification Value")
        verbose_name_plural = _("Product Specification Values")

    def __str__(self):
        return self.value


class ProductImage(models.Model):
    """
    The Product Image table.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_image")
    image = models.ImageField(
        verbose_name=_("image"),
        help_text=_("Upload a product image"),
        upload_to="images/products_images/",
        default="images/products_images//default.png",
    )
    alt_text = models.CharField(
        verbose_name=_("Alturnative text"),
        help_text=_("Please add alturnative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    rating = models.FloatField(default=0,)
    comment = models.TextField(max_length=1000,default="",blank=False) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.comment
    