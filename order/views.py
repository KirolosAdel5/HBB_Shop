from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderSerializer,CreateOrderSerializer
from .models import Order
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError

class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "post", "delete", "options", "head"]
    
    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
            
    def create(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                serializer = CreateOrderSerializer(data=request.data, context={"user_id": self.request.user.id})
                serializer.is_valid(raise_exception=True)
                order = serializer.save()
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                # Handle validation error
                return Response({"detail": "Please enter all required fields.", "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(owner=user)
