from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    create_review,
    delete_review,CategoryImageListBySlug,
    ProductSpecificationViewSet
    )
from rest_framework import urls

app_name = "store"

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product-specifications', ProductSpecificationViewSet, basename='product-specifications')


urlpatterns = [
    path('', include(router.urls)), 
    path('categories/retrieve_category_items/<str:identifier>/', CategoryViewSet.as_view({'get': 'retrieve_category_items'}), name='retrieve_category_items'),
    path('categorieslevel0/', CategoryViewSet.as_view({'get': 'list_parent'}), name='list_top_level'),
    path('categorieslevel1/', CategoryViewSet.as_view({'get': 'list_top_level'}), name='list_top_level'),
    path('products/<str:pk>/review/', create_review,name='create_review'),
    path('products/<str:pk>/review/delete/', delete_review,name='delete_review'),
    path('category-images/<slug:category_slug>/', CategoryImageListBySlug.as_view(), name='category-image-list-by-slug'),

    path('api-auth',include(urls)),
]