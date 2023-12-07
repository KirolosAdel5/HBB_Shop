from rest_framework import serializers
from .models import CustomUser ,WishlistItem,Address
from store.serializers import ProductSerializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['uuid_field', 'username', 'phone_number', 'password', 'otp', 'is_phone_verified']
        extra_kwargs = {
            'uuid_field': {'read_only': True},
            'password': {'write_only': True},
            'otp': {'write_only': True},
            'is_phone_verified': {'read_only': True},
        }

   
    def create(self, validated_data):
        
        username = validated_data['username']

        if ' ' not in username:
            # If it doesn't contain a space, set first_name to username and last_name to an empty string
            first_name = username
            last_name = ""
        else:
            first_name, last_name = username.split(" ", 1)
        # Replace spaces with underscores
        # username = generate_unique_username(first_name,last_name)
        
        user = CustomUser.objects.create_user(
            id=validated_data.get('uuid_field'),  # Include the UUID field
            username=validated_data['phone_number'],
            first_name = first_name ,
            last_name = last_name ,
            password=validated_data['password'],
            phone_number=validated_data['phone_number']
        )
        return user

# def generate_unique_username(first_name, last_name):
#     # Define a function to generate a unique username
#     # You can customize the logic for generating a unique username here

#     if first_name and last_name:
#         # Concatenate the first name and last name, replacing spaces with underscores
#         username = f"{first_name} {last_name}".replace(" ", "_").lower()

#         # Check if the username already exists and append a number if needed to make it unique
#         suffix = 1
#         while CustomUser.objects.filter(username=username).exists():
#             username = f"{first_name} {last_name}_{suffix}".replace(" ", "_").lower()
#             suffix += 1
#         return username
#     else:
#         return first_name  # Return the first name if last name is empty


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name','last_name', 'phone_number', 'username') 
        read_only_fields = ('username', 'phone_number')
class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = WishlistItem
        fields = ['product']
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['customer']
