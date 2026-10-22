from __future__ import annotations
from rest_framework import serializers
from category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id", "created_at", "created_by", "updated_at", "updated_by")