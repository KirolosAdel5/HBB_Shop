from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from users.models import CustomUser ,WishlistItem,Address
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from users.serializers import UserRegistrationSerializer ,UserLoginSerializer,UserSerializer,WishlistItemSerializer,AddressSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .utils import generate_otp , send_otp_via_sms
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from phonenumbers import NumberParseException
from datetime import datetime, timedelta
from django.db.models import Q
from store.models import Product
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.contrib.auth import authenticate

class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def create(self, request):
        phone_number = request.data.get("phone_number")
        
        try:
            existing_user = CustomUser.objects.filter(phone_number=phone_number).first()
        
            if existing_user:
                return Response({"message": "Email or phone number already registered"}, status=status.HTTP_409_CONFLICT)

            serializer = UserRegistrationSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # otp = generate_otp()
                # user.set_otp(otp)
                # send_otp_via_sms(phone_number, otp)

                # return Response({"details": "User registered successfully", "uuid": user.uuid_field,"phone_number":phone_number}, status=status.HTTP_201_CREATED)
                return Response({"details": "User registered successfully", "detail": serializer.data, "token": access_token}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"error": "Phone number already registered", "phone_number": phone_number}, status=status.HTTP_409_CONFLICT)
        except NumberParseException as e:
            return Response({"error": "Invalid phone number format. Please provide a valid phone number.", "phone_number": phone_number}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    @action(detail=False, methods=['POST'], url_path='resend-otp')
    def resend_otp_via_sms(self, request):
        uuid = request.data.get("user_id")
        try:
            user = CustomUser.objects.get(uuid_field=uuid)
            otp = generate_otp()
            user.set_otp(otp)
            send_otp_via_sms(user.phone_number, otp)
            return Response({"message": "OTP resent successfully", "phone_number": phone_number}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found with the provided phone number", "phone_number": phone_number}, status=status.HTTP_404_NOT_FOUND)

    
    @action(detail=False, methods=['POST'], url_path='verify-otp')
    def verify_otp(self, request, uuid):
        otp = request.data.get("otp")
        user = get_object_or_404(CustomUser, uuid_field=uuid)

        if user and user.validate_otp(otp):
            user.is_phone_verified = True
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "Phone number verified", "token": token.key}, status=status.HTTP_200_OK)

        return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        if request.user.is_authenticated:
            # Delete the authentication token for the user
            Token.objects.filter(user=request.user).delete()
            response_data = {"message": "You have been logged out."}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"message": "You are not authenticated."}
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


class UserLoginViewSet(viewsets.GenericViewSet):
    serializer_class = UserLoginSerializer
    
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            
            user = CustomUser.objects.filter(phone_number=phone_number).first()
            
            if user is not None and user.check_password(password):
                user.last_login = timezone.now()
                user.save()
                # Perform any additional actions if needed (e.g., generate a token)
                # Return the authenticated user details if necessary
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                return Response({"message": "User login successfully.", "detail": serializer.data, "token": access_token}, status=status.HTTP_200_OK)


            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'  # Specify the lookup field as 'pk'

    def get_queryset(self):
        return CustomUser.objects.filter(pk=self.request.user.id)

    def get_object(self):
        return self.request.user
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

# class PasswordResetByMobileView(CreateAPIView):
#     serializer_class = PasswordResetByMobileSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         mobile_number = serializer.validated_data['mobile_number']
#         user = User.objects.filter(mobile_number=mobile_number).first()

#         if user:
#             # Generate and send password reset SMS
#             user.send_password_reset_sms()
#             return Response({"detail": "Password reset SMS sent successfully."}, status=status.HTTP_200_OK)
#         else:
#             return Response({"detail": "User not found with this mobile number."}, status=status.HTTP_404_NOT_FOUND)

class WishlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)


    @action(detail=False, methods=['get'])
    def list_wishlist(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, identifier=None):
        product = get_object_or_404(Product, Q(id=identifier) | Q(slug=identifier))

        # Check if the product already exists in the wishlist
        existing_wishlist_item = WishlistItem.objects.filter(user=request.user, product=product).first()

        if existing_wishlist_item:
            # If the product exists, remove it from the wishlist
            existing_wishlist_item.delete()
            return Response(
                {"message": "Product removed from wishlist"},
                status=status.HTTP_200_OK,
            )
        else:
            # If the product doesn't exist, add it to the wishlist
            wishlist_item = WishlistItem.objects.create(user=request.user, product=product)
            serializer = self.get_serializer(wishlist_item)
            # Return only the serialized representation of WishlistItem without nested ProductSerializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({"message":"address removed successfully"}, status=status.HTTP_204_NO_CONTENT)

    
    @action(detail=True, methods=['patch'])
    def set_default(self, request, pk=None):
        # Set the selected address as default for the customer
        address = self.get_object()
        Address.objects.filter(customer=request.user, default=True).update(default=False)
        address.default = True
        address.save()
        return Response({"message": "Address set as default"}, status=status.HTTP_200_OK)
