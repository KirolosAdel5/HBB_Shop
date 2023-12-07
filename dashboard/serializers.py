from rest_framework import serializers
from .models import OrderAnalytics
from order.models import Order,OrderStatus
from django.utils import timezone
from datetime import timedelta

class OrderAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAnalytics
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Get the filtered date range from the request
        request = self.context.get('request')
        date_filter = request.query_params.get('date_filter', 'all')
        

        # Check if date_filter is provided
        if date_filter == 'all':
            filtered_orders = Order.objects.all()
        else:
            filtered_orders = self.filter_orders_by_date(instance, date_filter)

        # Calculate counts for the specified date range and update existing keys
        representation['total_orders'] = filtered_orders.count()
        representation['completed_orders'] = filtered_orders.filter(status=OrderStatus.DELIVERED).count()
        representation['processing_orders'] = filtered_orders.filter(status=OrderStatus.PROCESSING).count()
        representation['cancelled_orders'] = filtered_orders.filter(status=OrderStatus.CANCELLED).count()

        return representation

    def filter_orders_by_date(self, order_analytics_instance, date_filter):
        # Get the date range based on the filter
        today = timezone.now().date()
        if date_filter == 'today':
            start_date = today
            end_date = today + timedelta(days=1)
        elif date_filter == 'yesterday':
            end_date = today
            start_date = end_date - timedelta(days=1)
        # Add more date filter cases as needed...

        # Filter orders based on the date range
        return Order.objects.filter(createAt__gte=start_date, createAt__lt=end_date)
