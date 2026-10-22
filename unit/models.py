from django.db import models
from django.conf import settings

# Create your models here.


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_units",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_units",
        null=True,
        blank=True,
    )
    
    
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Unit"
        verbose_name_plural = "Units"
    
    

    def __str__(self):
        return self.code