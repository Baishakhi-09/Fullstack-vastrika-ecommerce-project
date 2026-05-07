from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # JWT IMPORT

from .models import User, NewsletterSubscriber

# --------------- Signup Serializer --------------- #
class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, trim_whitespace=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name"]

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"].strip(),
            email=validated_data["email"].strip().lower(),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", "").strip(),
        )
    
# --------------- Custom Login JWT Serializer --------------- #    
class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                "first_name": self.user.first_name,
                "email": self.user.email,
                "role": self.user.role,
            }
        )
        return data
    
# --------------- Profile Serializer --------------- #
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
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
        ]
        read_only_fields = ["email"]
    
# --------------- Newsletter --------------- #   
class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()
    
class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ["id", "email", "is_active", "subscribed_at"]
        read_only_fields = ["id", "subscribed_at"]