from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import (
    validate_password,
)
from django.db import transaction

from rest_framework import serializers

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from .models import (
    NewsletterSubscriber,
    User,
)


# =========================================================
# HELPERS
# =========================================================
def normalize_email(
    email: str,
) -> str:
    """
    Normalize email address.
    """

    return email.strip().lower()


# =========================================================
# SIGNUP SERIALIZER
# =========================================================
class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        trim_whitespace=True,
    )

    email = serializers.EmailField(
        required=True,
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password",
            "first_name",
        ]

    # VALIDATION
    def validate_username(
        self,
        value: str,
    ) -> str:
        """
        Validate username uniqueness.
        """

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must contain at least 3 characters."
            )

        if " " in value:
            raise serializers.ValidationError(
                "Username cannot contain spaces."
            )

        if User.objects.filter(
            username__iexact=value,
        ).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(
        self,
        value: str,
    ) -> str:
        """
        Validate email uniqueness.
        """

        value = normalize_email(value)

        if User.objects.filter(
            email__iexact=value,
        ).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    # CREATE
    @transaction.atomic
    def create(
        self,
        validated_data: dict[str, Any],
    ) -> User:
        """
        Create and return a new user.
        """

        return User.objects.create_user(
            username=validated_data[
                "username"
            ].strip(),

            email=normalize_email(
                validated_data["email"]
            ),

            password=validated_data[
                "password"
            ],

            first_name=validated_data.get(
                "first_name",
                "",
            ).strip(),
        )


# =========================================================
# CUSTOM JWT TOKEN SERIALIZER
# =========================================================
class CustomTokenSerializer(
    TokenObtainPairSerializer
):
    username_field = User.USERNAME_FIELD

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Return JWT token response.
        """

        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": (
                self.user.first_name
            ),
            "email": self.user.email,
            "role": self.user.role,
        }

        return data


# =========================================================
# PROFILE SERIALIZER
# =========================================================
class ProfileSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User

        fields = [
            "first_name",
            "email",
            "phone",
            "alternate_phone",
            "gender",
            "address",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "pincode",
            "country",
            "profile_image",
        ]

        read_only_fields = [
            "email",
        ]

    # VALIDATION
    def validate_first_name(
        self,
        value: str,
    ) -> str:
        """
        Normalize first name.
        """

        return value.strip()

    def validate_city(
        self,
        value: str,
    ) -> str:
        """
        Normalize city.
        """

        return value.strip()

    def validate_state(
        self,
        value: str,
    ) -> str:
        """
        Normalize state.
        """

        return value.strip()

    def validate_country(
        self,
        value: str,
    ) -> str:
        """
        Normalize country.
        """

        return value.strip()


# =========================================================
# NEWSLETTER SUBSCRIBE SERIALIZER
# =========================================================
class NewsletterSubscribeSerializer(
    serializers.Serializer
):
    """
    Newsletter subscription serializer.
    """

    email = serializers.EmailField()

    def validate_email(
        self,
        value: str,
    ) -> str:
        """
        Validate newsletter email.
        """

        value = normalize_email(value)

        if NewsletterSubscriber.objects.filter(
            email__iexact=value,
        ).exists():
            raise serializers.ValidationError(
                "This email is already subscribed."
            )

        return value


# =========================================================
# NEWSLETTER SUBSCRIBER SERIALIZER
# =========================================================
class NewsletterSubscriberSerializer(
    serializers.ModelSerializer
):
    """
    Newsletter subscriber serializer.
    """

    class Meta:
        model = NewsletterSubscriber

        fields = [
            "id",
            "email",
            "is_active",
            "subscribed_at",
        ]

        read_only_fields = [
            "id",
            "subscribed_at",
        ]