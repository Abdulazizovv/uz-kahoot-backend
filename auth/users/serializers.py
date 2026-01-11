from __future__ import annotations

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema_field
from .models import User
from django.contrib.auth.password_validation import validate_password


PHONE_VALIDATOR = RegexValidator(r"^\+?[0-9]{7,15}$", "Telefon raqami noto'g'ri formatda")


# Telegram bot OTP auth serializers
class TelegramRequestOTPSerializer(serializers.Serializer):
    """Telegram user_id orqali OTP so'rash"""
    user_id = serializers.CharField(
        required=True,
        help_text="Telegram user ID (Example: '123456789')"
    )
    
    class Meta:
        examples = {
            'user_id': '123456789'
        }


class TelegramVerifyOTPSerializer(serializers.Serializer):
    """Telegram OTP tasdiqlash va JWT token olish"""
    otp = serializers.CharField(
        required=True,
        min_length=5,
        max_length=5,
        help_text="5 xonali OTP kod (Example: '12345')"
    )
    
    class Meta:
        examples = {
            'otp': '12345'
        }


class TokenResponseSerializer(serializers.Serializer):
    """JWT token javob serializer"""
    access = serializers.CharField(help_text="JWT access token (valid for 15 minutes)")
    refresh = serializers.CharField(help_text="JWT refresh token (valid for 30 days)")
    user = serializers.SerializerMethodField(help_text="User information")
    
    @extend_schema_field(serializers.DictField())
    def get_user(self, obj):
        user = obj.get('user')
        if user:
            return {
                'id': str(user.id),
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'user_type': user.user_type,
                'phone_verified': user.phone_verified,
            }
        return None
    
    class Meta:
        examples = {
            'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
            'user': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'phone_number': '+998901234567',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'user_type': 'student',
                'phone_verified': True
            }
        }


# Phone number based OTP auth serializers
class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    code = serializers.CharField(min_length=4, max_length=10)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "date_joined",
        ]


class RegisterRequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])


class RegisterConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    code = serializers.CharField(min_length=4, max_length=10)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value: str):
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    password = serializers.CharField(write_only=True)
    branch_id = serializers.UUIDField(required=False, allow_null=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    code = serializers.CharField(min_length=4, max_length=10)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value: str):
        validate_password(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value: str):
        validate_password(value)
        return value


class PhoneCheckSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])


class PhoneVerificationRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])


class PhoneVerificationConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    code = serializers.CharField(min_length=4, max_length=10)


class PasswordSetSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value: str):
        validate_password(value)
        return value


def get_tokens_for_user(user):
    """User uchun JWT tokenlarni yaratadi"""
    refresh = RefreshToken.for_user(user)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user
    }
    