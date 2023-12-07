from rest_framework import serializers
from store.serializers import ProductSerializer
from.models import Order,OrderItem
from basket.models import Cart,Cartitems
from django.db import transaction
from users.models import Address
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem 
        fields = ["id", "product", "quantity","color","size"]
        


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order 
        fields = ['id', 'createAt', 'status', 'owner', 'address', 'payment_status', 'payment_mode', 'orderitems']
        
        
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    address_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    address_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This cart_id is invalid")
        
        elif not Cartitems.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Sorry your cart is empty")
        
        return cart_id
    
    
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            address_id = self.validated_data["address_id"].id  # Extract address_id
            user_id = self.context["user_id"]
            order = Order.objects.create(owner_id=user_id, address_id=address_id)
            cartitems = Cartitems.objects.filter(cart_id=cart_id)
            orderitems = [
                OrderItem(order=order, 
                    product=item.product, 
                    quantity=item.quantity,
                    color=item.color,
                    size=item.size
                    )
            for item in cartitems
            ]
            OrderItem.objects.bulk_create(orderitems)
            # Cart.objects.filter(id=cart_id).delete()
            cartitems.delete() 
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order 
        fields = ["status"]
