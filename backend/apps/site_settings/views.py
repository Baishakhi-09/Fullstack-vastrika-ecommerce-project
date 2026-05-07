from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SettingLevel, SettingGroup, SettingField, SettingFile
from .seed_settings import create_default_settings
from .serializers import (
    SettingLevelSerializer,
    SettingGroupSerializer,
    SettingUpdateSerializer,
)


# -------------------- SETTING TREE API -------------------- #
class SettingTreeAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        create_default_settings()

        levels = (
            SettingLevel.objects
            .filter(is_active=True)
            .prefetch_related(
                "groups",
                "groups__fields",
                "groups__fields__uploaded_file",
            )
            .order_by("order", "name")
        )

        serializer = SettingLevelSerializer(
            levels,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "message": "Settings tree loaded successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# -------------------- SETTING GROUP LIST API -------------------- #
class SettingListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        create_default_settings()

        groups = (
            SettingGroup.objects
            .filter(is_active=True)
            .select_related("level")
            .prefetch_related(
                "fields",
                "fields__uploaded_file",
            )
            .order_by("level__order", "order", "name")
        )

        serializer = SettingGroupSerializer(
            groups,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "message": "Settings loaded successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# -------------------- SINGLE SETTING GROUP API -------------------- #
class SettingGroupDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, group_key):
        create_default_settings()

        group = get_object_or_404(
            SettingGroup.objects
            .filter(is_active=True)
            .select_related("level")
            .prefetch_related(
                "fields",
                "fields__uploaded_file",
            ),
            key=group_key,
        )

        serializer = SettingGroupSerializer(
            group,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "message": "Setting group loaded successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# -------------------- SETTING UPDATE API -------------------- #
class SettingUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    @transaction.atomic
    def post(self, request):
        serializer = SettingUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Invalid settings data.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        settings_data = serializer.validated_data["settings"]

        updated_settings = []
        errors = {}

        for key, value in settings_data.items():
            try:
                field = SettingField.objects.select_related("group").get(
                    key=key,
                    is_active=True,
                )
            except SettingField.DoesNotExist:
                errors[key] = "Setting field not found."
                continue
            except SettingField.MultipleObjectsReturned:
                errors[key] = (
                    "Multiple settings found with this key. "
                    "Use unique keys or update by group-specific endpoint."
                )
                continue

            if field.field_type == SettingField.FieldType.FILE:
                continue

            if field.is_required and value in [None, ""]:
                errors[key] = f"{field.label} is required."
                continue

            if field.field_type == SettingField.FieldType.TOGGLE:
                value = str(value).lower()
                value = "true" if value in ["true", "1", "yes", "on"] else "false"

            field.value = "" if value is None else str(value)
            field.full_clean()
            field.save(update_fields=["value"])

            updated_settings.append(
                {
                    "key": field.key,
                    "value": field.get_value(),
                }
            )

        if errors:
            transaction.set_rollback(True)

            return Response(
                {
                    "success": False,
                    "message": "Some settings could not be updated.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "Settings updated successfully.",
                "updated_settings": updated_settings,
            },
            status=status.HTTP_200_OK,
        )


# -------------------- SETTING FILE UPLOAD API -------------------- #
class SettingFileUploadAPIView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        key = request.data.get("key")
        uploaded_file = request.FILES.get("file")

        if not key:
            return Response(
                {
                    "success": False,
                    "message": "Setting key is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploaded_file:
            return Response(
                {
                    "success": False,
                    "message": "File is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            field = SettingField.objects.get(
                key=key,
                field_type=SettingField.FieldType.FILE,
                is_active=True,
            )
        except SettingField.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "File setting field not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except SettingField.MultipleObjectsReturned:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Multiple file settings found with this key. "
                        "Please make setting keys globally unique."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        setting_file, _ = SettingFile.objects.update_or_create(
            field=field,
            defaults={
                "file": uploaded_file,
            },
        )

        field.value = setting_file.file.url
        field.full_clean()
        field.save(update_fields=["value"])

        return Response(
            {
                "success": True,
                "message": "File uploaded successfully.",
                "data": {
                    "key": field.key,
                    "file_url": request.build_absolute_uri(setting_file.file.url),
                },
            },
            status=status.HTTP_200_OK,
        )