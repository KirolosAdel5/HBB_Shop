from chartjs.views.lines import BaseLineChartView
from rest_framework import viewsets , permissions
from rest_framework.response import Response
from .models import OrderAnalytics 
from order.models import Order ,OrderStatus,OrderItem
from .serializers import OrderAnalyticsSerializer
from .permissions import IsAdminUser
from .filters import DateFilterBackend
from django.db.models import F
from datetime import datetime, timedelta
from django.http import JsonResponse
from users.models import CustomUser
from django.utils import timezone
from django.db.models import Sum, F, FloatField

class OrderAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderAnalytics.objects.all()
    serializer_class = OrderAnalyticsSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DateFilterBackend]

    def list(self, request, *args, **kwargs):
        # Create or get OrderAnalytics instance
        order_analytics_instance, created = OrderAnalytics.objects.get_or_create(pk=1)

        # Update analytics
        order_analytics_instance.update_analytics()

        # Serialize data and return as JSON
        serializer = self.get_serializer(order_analytics_instance, context={'request': request})
        return Response(serializer.data)

class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return labels for the x-axis (individual days)."""
        # Fetch the latest analytics data before generating the chart
        order_analytics_instance, created = OrderAnalytics.objects.get_or_create(pk=1)
        order_analytics_instance.update_analytics()

        # Get today's date
        today = datetime.now().date()

        # Generate labels for the last 20 days with day and month format
        labels = [(today - timedelta(days=i)).strftime("%m/%d") for i in range(19, -1, -1)]  # Last 20 days

        return labels

    def get_providers(self):
        """Return names of datasets."""
        return ["Total Orders", "Completed Orders", "Processing Orders", "Cancelled Orders"]

    def get_data(self):
        """Return datasets to plot."""
        # Fetch the latest analytics data before generating the chart
        order_analytics_instance, created = OrderAnalytics.objects.get_or_create(pk=1)

        # Retrieve actual values for each day
        total_orders_data = []
        completed_orders_data = []
        processing_orders_data = []
        cancelled_orders_data = []

        for date in self.get_labels():
            # Update analytics for the specific day
            order_analytics_instance.update_analytics(date=date)

            total_orders_data.append(order_analytics_instance.total_orders)
            completed_orders_data.append(order_analytics_instance.completed_orders)
            processing_orders_data.append(order_analytics_instance.processing_orders)
            cancelled_orders_data.append(order_analytics_instance.cancelled_orders)


        return [
            total_orders_data,
            completed_orders_data,
            processing_orders_data,
            cancelled_orders_data,
        ]

line_chart_json = LineChartJSONView.as_view()

def dash_board_json(request):
    # Fetch OrderAnalytics data
    order_analytics_instance, _ = OrderAnalytics.objects.get_or_create(pk=1)
    order_analytics_instance.update_analytics()

    # Get today's date
    today = timezone.localdate()

    

    # Get the first and last day of the current month
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Get the first and last day of the previous month
    first_day_of_last_month = (first_day_of_month - timedelta(days=1)).replace(day=1)
    last_day_of_last_month = first_day_of_month - timedelta(days=1)

    two_months_ago_start = (today - timedelta(days=60)).replace(day=1)
    two_months_ago_end = today.replace(day=1) - timedelta(days=1)
    
    # Calculate total sales for the current month with status 'Delivered'
    total_sales_month = OrderItem.objects.filter(
        order__createAt__range=(first_day_of_month, last_day_of_month),
        order__status=OrderStatus.DELIVERED
    ).aggregate(
        total_sales=Sum(F('quantity') * F('product__regular_price'), output_field=FloatField())
    )['total_sales'] or 0

    # Calculate total sales for today with status 'Delivered'
    total_sales_today = OrderItem.objects.filter(
        order__createAt__date=today,
        order__status=OrderStatus.DELIVERED
    ).aggregate(
        total_sales=Sum(F('quantity') * F('product__regular_price'), output_field=FloatField())
    )['total_sales'] or 0

    # Calculate total sales for yesterday with status 'Delivered'
    total_sales_yesterday = OrderItem.objects.filter(
        order__createAt__date=today - timedelta(days=1),
        order__status=OrderStatus.DELIVERED
    ).aggregate(
        total_sales=Sum(F('quantity') * F('product__regular_price'), output_field=FloatField())
    )['total_sales'] or 0

    # Calculate total sales for all time with status 'Delivered'
    total_sales_all_time = OrderItem.objects.filter(
        order__status=OrderStatus.DELIVERED
    ).aggregate(
        total_sales=Sum(F('quantity') * F('product__regular_price'), output_field=FloatField())
    )['total_sales'] or 0
    
    total_sales_two_months_ago = OrderItem.objects.filter(
        order__createAt__date__range=[two_months_ago_start, two_months_ago_end],
        order__status=OrderStatus.DELIVERED
    ).aggregate(
        total_sales_two_months_ago=Sum(F('quantity') * F('product__regular_price'), output_field=FloatField())
    )['total_sales_two_months_ago'] or 0


    
    # Prepare data for the template
    data = {
        'total_users': CustomUser.objects.count(),
        'total_orders': order_analytics_instance.total_orders,
        'completed_orders': order_analytics_instance.completed_orders,
        'processing_orders': order_analytics_instance.processing_orders,
        'cancelled_orders': order_analytics_instance.cancelled_orders,
        'total_sales_month': total_sales_month,
        'total_sales_today': total_sales_today,
        'total_sales_yesterday': total_sales_yesterday,
        'total_sales_all_time': total_sales_all_time,
        "total_sales_two_months_ago":total_sales_two_months_ago,
    }

    return JsonResponse(data)

class SalesLineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return labels for the x-axis (individual days)."""
        # Fetch the latest analytics data before generating the chart
        order_analytics_instance, created = OrderAnalytics.objects.get_or_create(pk=1)
        order_analytics_instance.update_analytics()

        # Get today's date
        today = datetime.now().date()

        # Generate labels for the last 20 days with day and month format in 'YYYY-MM-DD' format
        labels = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)] 

        return labels

    def get_providers(self):
        """Return names of datasets."""
        return ["Total Sales"]

    def get_data(self):
        """Return datasets to plot."""
        # Fetch the latest analytics data before generating the chart
        order_analytics_instance, created = OrderAnalytics.objects.get_or_create(pk=1)

        # Retrieve actual values for each day
        total_sales_data = []

        for date in self.get_labels():
            # Update analytics for the specific day

            # Calculate total sales for the day by summing the prices of delivered order items
            total_sales = OrderItem.objects.filter(
                order__createAt__date=date,
                order__status=OrderStatus.DELIVERED
            ).aggregate(
                total_sales=Sum(F('quantity') * F('product__regular_price'), output_field=FloatField())
            )['total_sales'] or 0

            total_sales_data.append(total_sales)

        return [total_sales_data]

sales_line_chart_json = SalesLineChartJSONView.as_view()