from django.db import models

class DiscountType(models.TextChoices):
    NONE = "NONE", "None"
    PERCENTAGE = "PERCENTAGE", "Percentage"
    FIXED = "FIXED", "Fixed Amount"
    



class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    PROCESSING = "PROCESSING", "Processing"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"