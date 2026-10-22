from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers

from users.models import UserProfile, User
from users.choices import UserRoleChoices


from annai_candles_be.file_handler import build_file_url, upload_file_to_s3

from annai_candles_be import constant as acb_constant




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    
    def validate(self, attrs):
        username_value = (attrs.get("username") or "").strip().lower()
        password = attrs.get("password")
        request = self.context.get("request")
        
        if not username_value:
            raise serializers.ValidationError(
                {"message": "Username is required."}
            )           
        
        
        user = authenticate(
            request=request,
            username=username_value,
            password=password,
        )
        if user is None:
            raise serializers.ValidationError(
                {"message": "Invalid username or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError({"message": "User account is inactive."})

        attrs["user"] = user
        return attrs
    
    


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Refresh token is required.")
        return value
    
    



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("file_name", "file_ext")
        
    def to_representation(self, instance):
        return {
            'file_url' : build_file_url(instance, acb_constant.S3_USER_FOLDER_NAME)
        } 



class UserDetailSerializer(serializers.ModelSerializer):    
    user_profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "user_uuid",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "is_active",
            "created_at",
            "updated_at",
            "user_profile"
        )
        
        


class AddNewMemberSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField()
    role = serializers.CharField()
    
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value
    
    
    def validate_role(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Role required.")

        return value
    
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        phone = validated_data.pop("phone")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        role = validated_data.pop("role")
        
        
        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        
        request = self.context["request"]
        
        UserProfile.objects.create(user=user, created_by=request.user)
        
        
        return user




class UpdateMemberSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    email = serializers.EmailField(required=False,allow_blank=True,allow_null=True)
    
    
    def validate_phone(self, value):
        user = self.instance

        if User.objects.filter(phone=value).exclude(
            pk=user.pk
        ).exists():
            raise serializers.ValidationError(
                "This phone number is already registered."
            )

        return value

    def validate_email(self, value):
        if value:
            user = self.instance
            value = value.strip().lower()

            if User.objects.filter(
                email__iexact=value
            ).exclude(pk=user.pk).exists():
                raise serializers.ValidationError(
                    "This email address is already registered."
                )

        return value
    
    
    def validate_role(self, value):
        value = (value or "").strip().upper()

        if not value:
            raise serializers.ValidationError("Role required.")

        if value not in UserRoleChoices.values:
            allowed = ", ".join(UserRoleChoices.values)
            raise serializers.ValidationError(
                f"Invalid role. Allowed values: {allowed}."
            )

        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if "phone" in validated_data:
            instance.username = validated_data["phone"]

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance
    
    
    







class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150,required=False)
    last_name = serializers.CharField(max_length=150,required=False)
    email = serializers.EmailField(required=False,allow_blank=True,allow_null=True)
    phone = serializers.CharField(max_length=20,required=False)
    image = serializers.FileField(required=False,allow_null=True, write_only=True)
    
    
    def validate(self, attrs):
        user = self.instance

        if "email" in attrs:
            email = attrs["email"]
            email = email.strip().lower() if email else None
            attrs["email"] = email

            if email and email != (user.email or "").lower():
                if User.objects.filter(email__iexact=email).exclude(
                    pk=user.pk
                ).exists():
                    raise serializers.ValidationError({
                        "email": "This email is already registered."
                    })

        if (
            "phone" in attrs
            and attrs["phone"] != user.phone
        ):
            phone = attrs["phone"]

            if User.objects.filter(phone=phone).exclude(
                pk=user.pk
            ).exists():
                raise serializers.ValidationError({
                    "phone": "This phone number is already registered."
                })

            if User.objects.filter(username=phone).exclude(
                pk=user.pk
            ).exists():
                raise serializers.ValidationError({
                    "phone": (
                        "This phone number cannot be used because "
                        "the corresponding username is already taken."
                    )
                })

        if not attrs:
            raise serializers.ValidationError(
                "Provide at least one field to update."
            )

        return attrs

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        
        changed_fields = []

        for field, value in validated_data.items():
            if getattr(instance, field) != value:
                setattr(instance, field, value)
                changed_fields.append(field)

        if "phone" in validated_data:
            if instance.username != instance.phone:
                instance.username = instance.phone
                changed_fields.append("username")               
        

        if image is not None:
            profile, _ = UserProfile.objects.get_or_create(
                user=instance
            )

            file_name, file_ext = upload_file_to_s3(
                image,
                acb_constant.S3_USER_FOLDER_NAME,
                instance.id
            )

            profile.file_name = file_name
            profile.file_ext = file_ext
            profile.save(
                update_fields=[
                    "file_name",
                    "file_ext",
                    "updated_at",
                ]
            )

        if changed_fields:
            instance.save(update_fields=changed_fields + ["updated_at"])

        return instance


        
        
        
        