from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views
app_name = 'basket'

router = DefaultRouter()
router.register("carts", views.CartViewSet)

cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")
urlpatterns = [
path('', include(router.urls)),
path("", include(cart_router.urls)),

]