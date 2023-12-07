from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework import urls
from .views import OrderViewSet
app_name = "order"

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")


urlpatterns = [
path('', include(router.urls)),

]