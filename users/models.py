from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings


from users.choices import UserRoleChoices, LoginActivityTypeChoices



class User(AbstractUser):

    user_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.SALESMAN,
    )
    phone = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)
        verbose_name = "User"
        verbose_name_plural = "Users"
        
    
    
    def save(self, *args, **kwargs):
        if self.email == "":
            self.email = None

        super().save(*args, **kwargs)        
        
    
    def __str__(self) -> str:
        return f"{self.email} ({self.role})"
    
    
    

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile",
    )
    file_name = models.UUIDField(null=True, blank=True)
    file_ext = models.CharField(max_length=10, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_user_profile",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_user_profile",
        null=True,
        blank=True,
    )
    
    
    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
        
        
        

class UserLoginActivity(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_activities",
    )
    activity_type = models.CharField(
        max_length=16,
        choices=LoginActivityTypeChoices.choices,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at", "-id")
        verbose_name = "User Login Activity"
        verbose_name_plural = "User Login Activities"