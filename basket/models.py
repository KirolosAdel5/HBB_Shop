from django.db import models
from store.models import Product
from django.contrib.auth.models import User
import uuid
from users.models import CustomUser
class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')

    def __str__(self):
        return str(self.id)

class Cartitems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='cartitems')
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=20)  # Color is required
    size = models.CharField(max_length=20)   # Size is required

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"