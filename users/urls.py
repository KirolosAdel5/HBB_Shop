from django.urls import path,include
from rest_framework.routers import DefaultRouter
from users.views import (
UserViewSet ,
UserLoginViewSet,
CurrentUserViewSet,
WishlistItemViewSet,
AddressViewSet
)
from rest_framework import urls
from . import views

app_name = "users"
router = DefaultRouter()
router.register(r'register', UserViewSet, basename='user-register')
router.register(r'login', UserLoginViewSet, basename='user-login')
router.register(r'users/me', CurrentUserViewSet, basename='user-info')
router.register(r'wishlist', WishlistItemViewSet, basename='wishlistitem')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('register/verify-otp/<str:uuid>/', views.UserViewSet.as_view({'post': 'verify_otp'}), name='verify-otp'),
    path('resend-otp/', UserViewSet.as_view({'post': 'resend_otp_via_sms'}), name='resend-otp'),
    path('logout/', views.UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('wishlist/add_to_wishlist/<identifier>/', WishlistItemViewSet.as_view({'post': 'add_to_wishlist'}), name='add_to_wishlist'),
    path('', include(router.urls)),

    path('api-auth',include(urls)),
]