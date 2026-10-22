from django.db import models


class UserRoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    SALESMAN = "SALESMAN", "Salesman"
    
    
    

class LoginActivityTypeChoices(models.TextChoices):
    """User login / logout activity types."""

    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"