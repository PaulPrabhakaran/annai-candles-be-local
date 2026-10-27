from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from django.utils.timezone import now

from category.models import Category
from products.models import Product, ProductUnitPrice, ProductPriceForCustomer
from unit.models import Unit

from customer.models import Customer
from customer.serializers import CustomerSerializer
from unit.serializers import UnitSerializer




class ProductUnitPriceInputSerializer(serializers.Serializer):
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all()
    )

    manufacturing_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )

    status = serializers.BooleanField(required=False)
    
    



class ProductUnitPriceOutputSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(
        source="unit.name",
        read_only=True,
    )

    class Meta:
        model = ProductUnitPrice
        fields = [
            "id",
            "unit",
            "unit_name",
            "manufacturing_cost",
            "price",
            "status",
        ]    





class ProductSerializer(serializers.ModelSerializer):    
    
    unit_price = ProductUnitPriceInputSerializer(
        many=True,
        required=False
    )


    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "serial_number",
            "hsn_code",
            "description",
            "status",
            "unit_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        
    
    
    
    def validate_name(self, value):
        
        value = value.strip()
        
        product = Product.objects.filter(name__iexact=value)
        
        if self.instance:
            product = product.exclude(id=self.instance.id)
            
        if product.exists():
            raise serializers.ValidationError(
                "A product with this name already exists."
            )
        
        return value
    
    
    def validate_category(self, category):
        if category is not None and not category.status:
            raise serializers.ValidationError("Cannot assign an inactive category to a product.")
        return category    
    

    def validate_unit_price(self, value):
        unit_ids = [item["unit"].pk for item in value]

        if len(unit_ids) != len(set(unit_ids)):
            raise serializers.ValidationError(
                "The same unit cannot be included more than once."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        unit_price = validated_data.pop("unit_price", [])

        request = self.context.get("request")
        user = request.user if request else None

        for item in unit_price:
            unit = item["unit"]
            
            if not unit.status:
                raise serializers.ValidationError({
                    "unit_price": [
                        f"Unit '{unit.name}' is inactive. "
                        "Please select an active unit."
                    ]
                })

        product = Product.objects.create(
            **validated_data,
            created_by=user
        )

        ProductUnitPrice.objects.bulk_create([
            ProductUnitPrice(
                product=product,
                unit=item["unit"],
                manufacturing_cost=item.get(
                    "manufacturing_cost", 0
                ),
                price=item.get("price", 0),
                created_by=user
            )
            for item in unit_price
        ])

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        unit_price = validated_data.pop("unit_price", None)

        request = self.context.get("request")
        user = request.user if request else None

        if validated_data:
            for field, value in validated_data.items():
                setattr(instance, field, value)

            instance.updated_by = user
            instance.save()

        if unit_price is None:
            return instance

        existing_prices = {
            item.unit_id: item
            for item in ProductUnitPrice.objects.filter(
                product=instance
            ).select_related("unit")
        }

        to_create = []
        to_update = []

        for item in unit_price:
            unit = item["unit"]
            existing = existing_prices.get(unit.pk)

            if existing:
                effective_status = item.get(
                    "status",
                    existing.status,
                )
            else:
                effective_status = True

            if effective_status and not unit.status:
                raise serializers.ValidationError({
                    "unit_price": [
                        f"Unit '{unit.name}' is inactive. "
                        "An active unit is required."
                    ]
                })
                
            
            
            
            if existing:
                for field in (
                    "manufacturing_cost",
                    "price",
                    "status",
                ):
                    if field in item:
                        setattr(existing, field, item[field])

                existing.updated_by = user
                existing.updated_at = now()
                to_update.append(existing)

            else:
                to_create.append(
                    ProductUnitPrice(
                        product=instance,
                        unit=unit,
                        manufacturing_cost=item.get("manufacturing_cost", 0),
                        price=item.get("price", 0),
                        status=item.get("status", True),
                        created_by=user
                    )
                )

        
        
        if to_update:
            ProductUnitPrice.objects.bulk_update(
                to_update,
                fields=[
                    "manufacturing_cost",
                    "price",
                    "status",
                    "updated_by",
                    "updated_at",
                ],
            )

        if to_create:
            ProductUnitPrice.objects.bulk_create(to_create)

        return instance
    
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["unit_price"] = ProductUnitPriceOutputSerializer(
            instance.unit_prices.all(),
            many=True
        ).data
        
        data["category"] = (
            ProductCategorySerializer(instance.category).data
            if instance.category
            else None
        )

        return data




class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = fields




class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = "__all__"
        
    
    





class ProductUnitPriceDetailSerializer(serializers.Serializer):
    product = ProductListSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    
    class Meta:
        model = ProductUnitPrice
        fields = ("id", "product", "unit", "manufacturing_cost", "price", "status")


    


class CustomerPriceItemSerializer(serializers.Serializer):
    unit_price = serializers.PrimaryKeyRelatedField(
        queryset=ProductUnitPrice.objects.all()
    )
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    def validate_unit_price(self, value):
        if not value.status:
            raise serializers.ValidationError(
                f"This unit price {value.id} is inactive."
            )

        return value


class AssignCustomerPricesSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all()
    )
    prices = CustomerPriceItemSerializer(
        many=True,
        allow_empty=False,
    )

    def validate_prices(self, value):
        unit_price_ids = [
            item["unit_price"].id for item in value
        ]

        if len(unit_price_ids) != len(set(unit_price_ids)):
            raise serializers.ValidationError(
                "Duplicate unit_price IDs are not allowed."
            )

        return value        
        
    
    
    
    
class ProductPriceForCustomerResponseSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    unit_price = ProductUnitPriceDetailSerializer(read_only=True)
    
    class Meta:
        model = ProductPriceForCustomer
        fields = "__all__"
        
        