from rest_framework import serializers
from .models import Cart, Cartitems
from store.serializers import ProductSerializer
from store.models import Product
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    sub_total = serializers.SerializerMethodField( method_name="total")
    class Meta:
        model= Cartitems
        fields = ["id", "cart", "product", "quantity", "sub_total","color","size"]
        
    
    def total(self, cartitem:Cartitems):
        return cartitem.quantity * cartitem.product.regular_price
    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("There is no product associated with the given ID")

        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"] 
        quantity = self.validated_data["quantity"] 
        color = self.validated_data.get("color")
        size = self.validated_data.get("size")
        
        existing_cartitem = Cartitems.objects.filter(
            cart_id=cart_id,
            product_id=product_id,
            color=color,
            size=size
        ).first()

        if existing_cartitem:
            # If it exists, update the quantity
            existing_cartitem.quantity += quantity
            existing_cartitem.save()
            self.instance = existing_cartitem
        else:
            # If it doesn't exist, create a new Cartitem
            self.instance = Cartitems.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = Cartitems
        fields = ["id", "product_id", "quantity", "color", "size"]
       
class UpdateCartItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Cartitems
        fields = ["quantity"]
class CartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField(method_name='main_total')
    total_quantity = serializers.SerializerMethodField(method_name='calculate_total_quantity')

    class Meta:
        model = Cart
        fields = ["id", "items", "grand_total", "total_quantity"]
        
    def validate(self, data):
        user = self.context['request'].user

        # Check if the user already has a cart
        existing_cart = Cart.objects.filter(user=user).first()

        if existing_cart:
            # Return the details of the existing cart
            return CartSerializer(existing_cart).data

        return data
    def create(self, validated_data):
        # Since 'grand_total' is not a model field, remove it from the validated data
        validated_data.pop('grand_total', None)

        # Create a new Cart instance without saving it to the database
        cart = Cart(**validated_data)

        # Save the cart instance to the database
        cart.save()

        return cart

    def main_total(self, cart: Cart):
        items = cart.items.all()
        total = sum([item.quantity * item.product.regular_price for item in items])
        return total
    
    def calculate_total_quantity(self, instance):
        # Calculate the sum of quantities for all items in the cart
        total_quantity = sum(item.quantity for item in instance.items.all())
        return total_quantity