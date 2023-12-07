# from django.shortcuts import get_object_or_404
# from django.contrib.sessions.models import Session
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view,permission_classes
# from rest_framework.response import Response
# from .models import Basket, BasketItem
# from store.models import Product
# from .serializers import ProductSerializer, BasketItemSerializer
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin ,DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Cart,Cartitems
from .serializers import CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class CartViewSet(CreateModelMixin,RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    def create(self, request, *args, **kwargs):
        # Use the serializer to validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the user and check if they already have a cart
        user = self.request.user
        existing_cart = Cart.objects.filter(user=user).first()

        # If the user already has a cart, return its details
        if existing_cart:
            return Response(CartSerializer(existing_cart).data, status=status.HTTP_200_OK)

        # If the user doesn't have a cart, proceed with creating a new one
        serializer.save(user=user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # When creating a cart, check if the user is authenticated
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # For non-authenticated users, create a cart without a user
            cart = serializer.save()
            # Schedule the task to remove the cart after one day
            remove_expired_cart.apply_async(args=[cart.id], eta=timezone.now() + timedelta(days=1))
            
    def perform_destroy(self, instance):
        # Delete the cart only if it's not associated with any user
        if instance.user is None:
            instance.delete()
            return Response({"details": "Cart deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You are not allowed to delete this cart"}, status=status.HTTP_403_FORBIDDEN)



class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    
    @action(detail=False, methods=['post'])
    def clear_cart(self, request, cart_pk=None):
        try:
            cart = Cart.objects.get(pk=cart_pk)
            cart_items = Cartitems.objects.filter(cart=cart)
            cart_items.delete()
            return Response({"detail": "Cart cleared successfully"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        return Cartitems.objects.filter(cart_id=self.kwargs["cart_pk"])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer

        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}