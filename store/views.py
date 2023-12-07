from rest_framework import viewsets, generics,filters,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view,permission_classes

from django.shortcuts import get_object_or_404

from .models import Category, Product,Review ,CategoryImage,ProductSpecification
from .serializers import CategorySerializer, ProductSerializer ,ReviewSerializer,CategoryImageSerializer,ProductSpecificationSerializer,BrandSerializer
from .filters import ProductsFilter  # Import your custom filter
from rest_framework.permissions import IsAuthenticated ,IsAdminUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.http import Http404
from django.db.models import Avg
from django.db.models import Q

# Viewset for listing products
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 48  
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomProductPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any user to have read-only access
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow admin users to have full access
        return request.user and request.user.is_staff

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = ProductsFilter
    search_fields = ['title', 'description','category__name','product_type__name','brand']
    pagination_class = CustomPageNumberPagination
    permission_classes = [CustomProductPermission]
    # parser_classes = [MultiPartParser, FormParser]  # Allow file uploads
    lookup_field = 'identifier'  
    
    def get_queryset(self):
        queryset = Product.objects.all()

        # Get the 'sort' query parameter from the request
        sort_order = self.request.query_params.get('sort', None)

        # Apply sorting based on the 'sort' parameter
        if sort_order == 'max_to_min':
            queryset = queryset.order_by('-regular_price')
        elif sort_order == 'min_to_max':
            queryset = queryset.order_by('regular_price')

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        #self.perform_create(serializer)
        serializer.save(user=self.request.user)
        
        headers = self.get_success_headers(serializer.data)
        message = "Product created successfully"  # Your custom message

        return Response(
                    {"details": message, "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Print validation errors if any
        if serializer.errors:
            print(serializer.errors)

        self.perform_update(serializer)
        
        message = "Product updated successfully"  # Your custom message
        return Response({"details": message, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        message = "Product deleted successfully"  # Your custom message
        return Response({"details": message}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def brands(self, request):
        brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand='')

        serializer = BrandSerializer([{'name': brand} for brand in brands], many=True)

        return Response(serializer.data)
    
    def get_object(self):
        queryset = self.get_queryset()
        identifier = self.kwargs['identifier']
        
        # Check if the identifier is a digit (id) or a string (slug)
        try:
            if identifier.isdigit():
                return queryset.get(id=identifier)
            else:
                return queryset.get(slug=identifier)
        except Product.DoesNotExist:
            raise Http404("Product not found")
    

# Viewset for listing products in a category and its descendants
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CustomProductPermission]
    lookup_field = 'identifier'  
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return self.filter_queryset(self.get_category_queryset())

    def get_category_queryset(self):
        if self.action == 'list_top_level':
            return Category.objects.filter(level=1)
        elif self.action == 'list_parent':
            return Category.objects.filter(level=0)
        else:
            return Category.objects.all()

    @action(detail=True, methods=['get'])
    def list_top_level(self, request, *args, **kwargs):
        queryset = self.get_category_queryset()
        serializer = self.get_serializer(Category.objects.filter(level=1), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def list_parent(self, request, *args, **kwargs):
        queryset = self.get_category_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def retrieve_category_items(self, request, *args, **kwargs):
        category = self.get_object()
        products = Product.objects.filter(category__in=category.get_descendants(include_self=True))

        # Get the sort parameter from the query string (default to 'price')
        sort_param = request.query_params.get('sort', 'regular_price')

        # Determine the sorting order (default to ascending)
        sort_order = request.query_params.get('order', 'asc')

        # Validate sort_param
        valid_sort_fields = [field.name for field in Product._meta.get_fields()]
        if sort_param not in valid_sort_fields:
            return Response({'error': f'Invalid sort field: {sort_param}'}, status=status.HTTP_400_BAD_REQUEST)

        # Apply sorting based on the 'sort' parameter and 'order' parameter
        if sort_order.lower() == 'desc':
            products = products.order_by(f'-{sort_param}')
        else:
            products = products.order_by(sort_param)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    @action(detail=True, methods=['post'])
    def add_child(self, request, *args, **kwargs):
        parent_category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add the child category to the parent
        child_category = Category.objects.create(parent=parent_category, **serializer.validated_data)

        # Serialize the child category
        child_serializer = CategorySerializer(child_category)
        return Response({"details": "children added successfully",
                         "data" :child_serializer.data
                         }, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({"details": "Category created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"details": "Category updated successfully", "data": serializer.data})
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"details": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    def get_object(self):
        queryset = self.get_queryset()
        identifier = self.kwargs['identifier']

        try:
            if identifier.isdigit():
                return queryset.get(id=identifier)
            else:
                return queryset.get(slug=identifier)
        except Category.DoesNotExist:
            raise Http404("Category not found")

class CategoryImageListBySlug(generics.ListAPIView):
    serializer_class = CategoryImageSerializer

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        try:
            category = Category.objects.get(slug=category_slug)
            return CategoryImage.objects.filter(category=category)
        except Category.DoesNotExist:
            return CategoryImage.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    if pk.isdigit():
        product = get_object_or_404(Product, id=pk)
    else:
        product = get_object_or_404(Product, slug=pk)
    data = request.data
    review = product.reviews.filter(user=user)
    
    if not data.get('rating'):
        return Response({"rating": 'this is required'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not data.get('comment'):
        return Response({"comment": 'this is required'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    if int(data['rating']) <= 0 or int(data['rating']) > 5:
        return Response({"error": 'Please select between 1 to 5 only'},
                        status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = {'rating': data['rating'], 'comment': data['comment']}
        review.update(**new_review)

        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.rating = rating['avg_ratings']
        product.save()

        return Response({'details': 'Product review updated'})
    else:
        Review.objects.create(
            user=user,
            product=product,
            rating=data['rating'],
            comment=data['comment']
        )
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.rating = rating['avg_ratings']
        product.save()
        return Response({'details': 'Product review created'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    if pk.isdigit():
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        product = get_object_or_404(Product, slug=pk)
    review = product.reviews.filter(user=user)

    if review.exists():
        review.delete()
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0
            product.rating = rating['avg_ratings']
            product.save()
            return Response({'details': 'Product review deleted'})
    else:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    

class ProductSpecificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
