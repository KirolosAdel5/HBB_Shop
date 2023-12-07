from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .validators import username_validator,validate_password_complexity
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from phonenumbers import parse, format_number, PhoneNumberFormat
from django.conf import settings
from store.models import Product
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, numbers, and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    uuid_field = models.UUIDField(default=uuid.uuid4, unique=True) 
    phone_number = models.CharField(max_length=15,unique=True)
    password = models.CharField(
        'password',
        max_length=128,
        validators=[validate_password_complexity]  # Add the custom password validator
    )
    
    is_phone_verified = models.BooleanField(default=False)  
    otp = models.CharField(max_length=6, null=True, blank=True)  


    def __str__(self):
        return self.username
    
    def set_otp(self, otp):
        self.otp = otp
        self.save()
        
    def validate_otp(self, otp):
        return self.otp == otp
    

class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist: {self.product.title}"

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomUser, verbose_name=_("Customer"), on_delete=models.CASCADE)
    city = models.CharField(_("City"), max_length=150, default='DefaultCity')
    Area = models.CharField(_("Area"), max_length=150)
    building_details = models.CharField(_("Building Details (Building/House Number, Floor, Apartment Number)"), max_length=255,default="IRAQ",null=True)
    street_details = models.CharField(_("Street Details (Street Name/Number)"), max_length=255)
    landmark = models.CharField(_("Landmark"), max_length=255)
    full_name = models.CharField(_("Full Name"), max_length=150)
    phone = models.CharField(_("Mobile Phone Number"), max_length=50)
    
    HOME = 'home'
    WORK = 'work'
    ADDRESS_TYPE_CHOICES = [
        (HOME, 'Home'),
        (WORK, 'Work'),
    ]
    address_type = models.CharField(_("Address Type"), max_length=10, choices=ADDRESS_TYPE_CHOICES, default=HOME)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    default = models.BooleanField(_("Default"), default=False)


    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return str(_(self.city))

@receiver(post_save, sender=CustomUser)  # Use your user model here
def create_auth_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
        