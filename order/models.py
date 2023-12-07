from django.db import models
from store.models import Product
from django.conf import settings
from users.models import Address
from django.utils.translation import gettext_lazy as _

class OrderStatus(models.TextChoices):
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'
    

class PaymentStatus(models.TextChoices):
    PAID = 'Paid'
    UNPAID = 'Unpaid'

class PaymentMode(models.TextChoices):
    COD = 'COD'
    CARD = 'CARD'

class Order(models.Model):
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    payment_mode = models.CharField(max_length=30, choices=PaymentMode.choices, default=PaymentMode.COD)
    status = models.CharField(max_length=60, choices=OrderStatus.choices, default=OrderStatus.PROCESSING)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    createAt = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
    def save(self, *args, **kwargs):
        # Disconnect the post_save signal temporarily
        post_save.disconnect(order_post_save, sender=Order)

        # Check if the order status is changing to 'DELIVERED' or 'CANCELLED'
        if self.pk:  # Ensure that the order is not a new instance
            original_order = Order.objects.get(pk=self.pk)

            # Update stock when the order is marked as 'DELIVERED'
            if original_order.status != OrderStatus.DELIVERED and self.status == OrderStatus.DELIVERED:
                self._update_stock_on_delivery()

            # Return products to stock when the order is marked as 'CANCELLED'
            elif original_order.status != OrderStatus.CANCELLED and self.status == OrderStatus.CANCELLED:
                self._return_products_to_stock_on_cancellation()

        # Call the original save method
        super().save(*args, **kwargs)

        # Reconnect the post_save signal after saving
        post_save.connect(order_post_save, sender=Order)

    def _update_stock_on_delivery(self):
        # Update quantity and stock for each product in the order
        for order_item in self.orderitems.all():
            product = order_item.product
            if product:
                # Ensure that the ordered quantity is within the available stock
                if order_item.quantity <= product.stock:
                    # Reduce the quantity of OrderItem and update the stock of the product
                    product.stock -= order_item.quantity
                    product.save(update_fields=['stock'])
                else:
                    # Handle the case where the ordered quantity exceeds the available stock
                    # For now, let's just log a warning
                    import logging
                    logging.warning(f"Order {self.id}: Insufficient stock for product {product.id}")

    def _return_products_to_stock_on_cancellation(self):
        # Return the ordered quantity to stock for each product in the order
        for order_item in self.orderitems.all():
            product = order_item.product
            if product:
                # Increase the stock of the product
                product.stock += order_item.quantity
                product.save(update_fields=['stock'])

# Additional imports for the Order model and related constants
from django.db.models.signals import post_save
from django.dispatch import receiver

# Connect the save method to the post_save signal
@receiver(post_save, sender=Order)
def order_post_save(sender, instance, **kwargs):
    instance.save()
class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveSmallIntegerField(default=1)
    color = models.CharField(max_length=20, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.product) if self.product else 'No Product'
