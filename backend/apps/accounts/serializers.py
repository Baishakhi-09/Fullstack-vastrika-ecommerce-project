from django.db import transaction
from django.contrib.auth.password_validation import (
    validate_password,
)

from rest_framework import serializers
from rest_framework.validators import (
    UniqueValidator,
)

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from .models import (
    User,
    NewsletterSubscriber,
)


# =========================================================
# SIGNUP SERIALIZER
# =========================================================

class SignupSerializer(serializers.ModelSerializer):
    """
    User registration serializer.
    """

    username = serializers.CharField(
        required=True,
        trim_whitespace=True,
        min_length=3,
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=(
                    "Username already exists."
                ),
            ),
        ],
    )

    email = serializers.EmailField(
        required=True,
        trim_whitespace=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=(
                    "Email already exists."
                ),
            ),
        ],
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        trim_whitespace=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password",
            "first_name",
        )

    def validate_email(
        self,
        value: str,
    ) -> str:
        return value.strip().lower()

    @transaction.atomic
    def create(
        self,
        validated_data,
    ) -> User:
        return User.objects.create_user(
            username=validated_data[
                "username"
            ].strip(),

            email=validated_data[
                "email"
            ].strip().lower(),

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
    TokenObtainPairSerializer,
):
    """
    Custom JWT serializer.
    """

    username_field = User.USERNAME_FIELD

    def validate(
        self,
        attrs,
    ):
        data = super().validate(attrs)

        data.update({
            "user": {
                "id": self.user.id,
                "username": (
                    self.user.username
                ),
                "first_name": (
                    self.user.first_name
                ),
                "email": (
                    self.user.email
                ),
                "role": (
                    self.user.role
                ),
                "role_display": (
                    self.user.get_role_display()
                ),
            },
        })

        return data


# =========================================================
# PROFILE SERIALIZER
# =========================================================

class ProfileSerializer(
    serializers.ModelSerializer,
):
    """
    User profile serializer.
    """

    class Meta:
        model = User

        fields = (
            "first_name",
            "email",
            "phone",
            "alternate_phone",
            "gender",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "pincode",
            "country",
        )

        read_only_fields = (
            "email",
        )


# =========================================================
# NEWSLETTER SUBSCRIBE SERIALIZER
# =========================================================

class NewsletterSubscribeSerializer(
    serializers.Serializer,
):
    """
    Newsletter subscription serializer.
    """

    email = serializers.EmailField()

    default_error_messages = {
        "already_subscribed": (
            "This email is already "
            "subscribed."
        ),
    }

    def validate_email(
        self,
        value: str,
    ) -> str:

        email = value.strip().lower()

        if (
            NewsletterSubscriber.objects
            .filter(email__iexact=email)
            .exists()
        ):
            raise serializers.ValidationError(
                self.error_messages[
                    "already_subscribed"
                ]
            )

        return email


# =========================================================
# NEWSLETTER SUBSCRIBER SERIALIZER
# =========================================================

class NewsletterSubscriberSerializer(
    serializers.ModelSerializer,
):
    """
    Newsletter subscriber serializer.
    """

    class Meta:
        model = NewsletterSubscriber

        fields = (
            "id",
            "email",
            "is_active",
            "subscribed_at",
        )

        read_only_fields = (
            "id",
            "subscribed_at",
        )