from rest_framework import serializers

from decimal import Decimal

from customer.models import Customer
from products.models import Product
from unit.models import Unit

from orders.choices import DiscountType



class CreateOrderItemSeriazlier(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(status=True)
    )
    
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.filter(status=True)
    )
    
    qty = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01")
    )
    discount_type = serializers.ChoiceField(
        choices=DiscountType.choices,
        required=False,
        allow_null=True,
        default=DiscountType.NONE,
    )
    discount_value = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )
    
    
    def validate_discount_type(self, value):        
        if not value:
            return DiscountType.NONE        
        return value
    
    





class CreateOrderSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(status=True).all()
    )
    common_discount_type = serializers.ChoiceField(
        choices=DiscountType.choices,
        required=False,
        allow_null=True,
        default=DiscountType.NONE,
    )
    common_discount_value = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )
    common_discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )
    
    items = CreateOrderItemSeriazlier(
        many=True,
        allow_empty=False
    )
    
        
    
    def validate_common_discount_type(self, value):        
        if not value:
            return DiscountType.NONE        
        return value
    