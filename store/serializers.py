from rest_framework import serializers

from .models import Category, Product, ProductImage,Review,ProductSpecification,ProductSpecificationValue,CategoryImage

from users.models import WishlistItem
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text","is_feature"]

class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = '__all__'

    def to_representation(self, instance):
        # Exclude the 'category' field from the serialized data
        data = super().to_representation(instance)
        data.pop('category', None)
        return data

class CategorySerializer(serializers.ModelSerializer):
    category_images = CategoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["name", "slug","category_images"]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['children'] = CategorySerializer(instance.get_children(), many=True).data
        return representation

class ProductSpecificationValueSerializer(serializers.ModelSerializer):
    specification_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecificationValue
        fields = ['id', 'specification','specification_name', 'value']

    def get_specification_name(self, obj):
        return obj.specification.name
    def to_representation(self, instance):
        return {
            'specification_name': instance.specification.name,
            'value': instance.value
        }

class ProductSpecificationSerializer(serializers.Serializer):
    specification_values = ProductSpecificationValueSerializer(many=True, read_only=True, source='productspecificationvalue_set')

    class Meta:
        fields = ['id', 'name', 'specification_values']

    def to_representation(self, instance):
        specification_values = instance.productspecificationvalue_set.all()
        grouped_values = {}

        for spec_value in specification_values:
            spec_name = spec_value.specification.name
            if spec_name not in grouped_values:
                grouped_values[spec_name] = []

            grouped_values[spec_name].append(spec_value.value)

        return {
            'id': instance.id,
            'name': instance.name,
            'specification_values': [{'specification_name': key, 'values': values} for key, values in grouped_values.items()]
        }

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True)
    category = CategorySerializer(read_only=True)
    product_image = ImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(
            max_length=100000,
            allow_empty_file=False,
            use_url=False
        ),
        write_only=True
    )
    specification_values = ProductSpecificationValueSerializer(many=True, read_only=True)

    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)
    is_featured = serializers.SerializerMethodField(method_name='is_in_wishlist', read_only=True)


    class Meta:
        model = Product
        fields = ["id", "product_type", "category", "title", "description", "slug", "regular_price", "product_image", "category_name","specification_values" ,"rating","reviews", "uploaded_images","is_featured"]

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        uploaded_images = validated_data.pop('uploaded_images', None)
        specification_values_data = validated_data.pop('specification_values', [])

        if category_name:
            # Convert category name to category instance's primary key
            category_instance, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category_instance

        product = Product.objects.create(**validated_data)

        if uploaded_images:
            for image_data in uploaded_images:
                ProductImage.objects.create(product=product, image=image_data)

        # Create product specification values
        for spec_value_data in specification_values_data:
            ProductSpecificationValue.objects.create(product=product, **spec_value_data)

        return product

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Update specification_values in the representation
        representation['specification_values'] = [
            ProductSpecificationValueSerializer(item).to_representation(item)
            for item in instance.specification_values.all()
        ]

        return representation
    def is_in_wishlist(self, obj):
        # Check if the product is in the user's wishlist
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return WishlistItem.objects.filter(user=user, product=obj).exists()
        return False


class ReviewSerializer(serializers.ModelSerializer):
    
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    

    class Meta:
        model = Review
        fields = ["user",  "product","comment", "rating",]
        

class BrandSerializer(serializers.Serializer):
    name = serializers.CharField()
