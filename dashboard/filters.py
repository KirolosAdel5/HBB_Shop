# analytics/filters.py
from django.utils import timezone
from rest_framework import filters
from datetime import timedelta
from order.models import Order, OrderStatus

class DateFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        date_filter = request.query_params.get('date_filter', 'all')

        if date_filter == 'today':
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=1)
        elif date_filter == 'yesterday':
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=1)
        elif date_filter == 'current_week':
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif date_filter == 'current_month':
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        elif date_filter == 'last_week':
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif date_filter == 'last_month':
            today = timezone.now().date()
            end_date = today.replace(day=1) - timedelta(days=1)
            start_date = end_date.replace(day=1)
        elif date_filter == 'current_year':
            today = timezone.now().date()
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif date_filter == '3_months_later':
            today = timezone.now().date()
            start_date = today + timedelta(days=1)
            end_date = start_date + timedelta(days=90)
        elif date_filter == '6_months_later':
            today = timezone.now().date()
            start_date = today + timedelta(days=1)
            end_date = start_date + timedelta(days=180)
        else:
            start_date = None
            end_date = None

        if start_date and end_date:
            queryset = queryset.filter(createAt__gte=start_date, createAt__lt=end_date)

        return queryset
