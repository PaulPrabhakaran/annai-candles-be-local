from __future__ import annotations
from rest_framework import serializers
from unit.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = ("id", "created_at", "created_by", "updated_at", "updated_by")