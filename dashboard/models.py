from django.db import models
from store.models import Product
from users.models import Address
from django.conf import settings
from order.models import Order , OrderStatus
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.utils import timezone

class OrderAnalytics(models.Model):
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    processing_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    # Add more analytics fields as needed

    def update_analytics(self, date=None):
        # Update analytics based on Order model data for the specified date
        queryset = Order.objects.all()

        if date:
            # Convert the date to the correct format before filtering
            date_obj = datetime.strptime(date, "%m/%d").date().replace(year=timezone.now().year)
            queryset = queryset.filter(createAt__date=date_obj)

        self.total_orders = queryset.count()
        self.completed_orders = queryset.filter(status=OrderStatus.DELIVERED).count()
        self.processing_orders = queryset.filter(status=OrderStatus.PROCESSING).count()
        self.cancelled_orders = queryset.filter(status=OrderStatus.CANCELLED).count()

        # Save the updated analytics to the database
        self.save()
