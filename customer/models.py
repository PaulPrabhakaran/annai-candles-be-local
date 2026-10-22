from django.db import models
from django.conf import settings

# Create your models here.



class Customer(models.Model):
    name = models.CharField(max_length=300)
    store_name = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_customers",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_customers",
        null=True,
        blank=True,
    )
    
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"