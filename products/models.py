from django.db import models
from django.db.models.functions import Lower
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from category.models import Category
from unit.models import Unit

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    hsn_code = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_products",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_products",
        null=True,
        blank=True,
    )
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_product_name_ci",
                violation_error_message="A product with this name already exists.",
            ),
        ]






class ProductUnitPrice(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="unit_prices",
    )
    unit = models.ForeignKey(
        "unit.Unit",
        on_delete=models.PROTECT,
        related_name="product_prices",
    )
    manufacturing_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_product_unit_price",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_product_unit_price",
        null=True,
        blank=True,
    )
    
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Product Unit Price"
        verbose_name_plural = "Product Unit Prices"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "unit"],
                name="unique_product_unit_price",
            )
        ]
        
        
        


class ProductPriceForCustomer(models.Model):
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        related_name="special_prices",
    )
    product_unit = models.ForeignKey(
        "ProductUnitPrice",
        on_delete=models.CASCADE,
        related_name="customer_prices",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_product_price_for_customer",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_product_price_for_customer",
        null=True,
        blank=True,
    )
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Product Price For Customer"
        verbose_name_plural = "Product Price For Customers"
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "product_unit"],
                name="unique_customer_price",
            )
        ]
      
