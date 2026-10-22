from django.db import models
from django.db.models.functions import Lower
from django.conf import settings

# Create your models here.



class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_categories",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_categories",
        null=True,
        blank=True,
    )
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_category_name_ci",
                violation_error_message="A category with this name already exists.",
            ),
        ]        
        