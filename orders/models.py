from django.db import models
from customer.models import Customer
from django.conf import settings
from orders.choices import DiscountType

from products.models import Product
from unit.models import Unit


class Orders(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_items = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    sub_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    item_discount_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    common_discount_type = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.NONE,
    )

    common_discount_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    common_discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_orders",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        
        
        
        



class OrderItems(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    product_name = models.CharField(max_length=255)
    unit_name = models.CharField(max_length=100)

    qty = models.DecimalField(
        max_digits=12,
        decimal_places=3,
    )

    unit_price_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    
    
    sub_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.NONE,
    )

    discount_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"