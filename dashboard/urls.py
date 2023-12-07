from django.urls import path,include
from rest_framework.routers import DefaultRouter 
from .views import  line_chart_json ,dash_board_json,OrderAnalyticsViewSet,sales_line_chart_json

app_name = "dashboard"

router = DefaultRouter()
router.register(r'order-analytics', OrderAnalyticsViewSet, basename='order_analytics')


urlpatterns = [
    path('line-chart-json/', line_chart_json, name='line_chart_json'),
    path('sales_line_chart_json/', sales_line_chart_json, name='sales_line_chart_json'),
    path('dash_board_json/', dash_board_json, name='dash_board_json'),

    path('', include(router.urls)),

]
