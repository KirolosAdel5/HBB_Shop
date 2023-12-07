# filters.py
import django_filters
from .models import Product, Category, ProductSpecification, ProductSpecificationValue
from django.db.models import Q

class ProductSpecificationFilter(django_filters.FilterSet):
    class Meta:
        model = ProductSpecification
        fields = []

class ProductsFilter(django_filters.FilterSet):
    category_choices = Category().get_all_categories_choices()

    category = django_filters.ChoiceFilter(choices=category_choices, method='filter_category')
    keyword = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    price_min = django_filters.NumberFilter(field_name='regular_price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='regular_price', lookup_expr='lte')
    rating_list = django_filters.ChoiceFilter(
        choices=[
            ('top_rated', 'Top Rated'),
            ('less_rated', 'Less Rated'),
        ],
        method='filter_rating_list'
    )
    specification_values = django_filters.CharFilter(method='filter_specification_values')

    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Dynamically create filters for each ProductSpecification
    #     specifications = ProductSpecification.objects.all()
    #     for specification in specifications:
    #         field_name = f'specification_values__value__{specification.name}'

    #         # Retrieve distinct values for the current specification
    #         values = ProductSpecificationValue.objects.filter(specification=specification).values_list('value', flat=True).distinct()

    #         # Convert values to a list of tuples for choice filter
    #         choices = [(value, value) for value in values]

    #         # Create a ChoiceFilter for the current specification
    #         filter_field = django_filters.ChoiceFilter(field_name=field_name, label=specification.name, choices=choices)
            
    #         self.filters[field_name] = filter_field

    def filter_category(self, queryset, name, value):
        try:
            category = Category.objects.get(Q(name__iexact=value) | Q(slug__iexact=value))
            descendants = category.get_descendants(include_self=True)
            return queryset.filter(category__in=descendants)
        except Category.DoesNotExist:
            return queryset.none()

    
    def filter_top_rated(self, queryset, name, value):
        if value:
            return queryset.filter(rating__gte=4.5)  # Adjust the threshold as needed
        return queryset

    def filter_less_rated(self, queryset, name, value):
        if value:
            return queryset.filter(rating__lt=4.5)  # Adjust the threshold as needed
        return queryset

    def filter_rating_list(self, queryset, name, value):
        if value == 'top_rated':
            return self.filter_top_rated(queryset, name, True)
        elif value == 'less_rated':
            return self.filter_less_rated(queryset, name, True)
        return queryset
    
    def filter_specification_values(self, queryset, name, value):
        # Split the values by comma and filter products that have any of the specified specification values
        values = value.split(',')
        return queryset.filter(specification_values__value__in=values).distinct()

    class Meta:
        model = Product
        fields = ('price_min', 'price_max', 'category', 'product_type', 'keyword', 'rating_list', 'brand','tags')
