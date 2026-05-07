from rest_framework import serializers

from .models import SettingLevel, SettingGroup, SettingField, SettingFile


# -------------------- SETTING FILE SERIALIZER -------------------- #
class SettingFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SettingFile
        fields = [
            "id",
            "file",
            "file_url",
            "uploaded_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")

        if not obj.file:
            return None

        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url


# -------------------- SETTING FIELD SERIALIZER -------------------- #
class SettingFieldSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()
    uploaded_file = SettingFileSerializer(read_only=True)

    class Meta:
        model = SettingField
        fields = [
            "id",
            "label",
            "key",
            "field_type",
            "placeholder",
            "help_text",
            "default_value",
            "value",
            "current_value",
            "options",
            "is_required",
            "is_active",
            "order",
            "uploaded_file",
        ]

    def get_current_value(self, obj):
        if obj.field_type == SettingField.FieldType.FILE:
            uploaded_file = getattr(obj, "uploaded_file", None)
            if uploaded_file and uploaded_file.file:
                request = self.context.get("request")
                if request:
                    return request.build_absolute_uri(uploaded_file.file.url)
                return uploaded_file.file.url

        return obj.get_value()


# -------------------- SETTING GROUP SERIALIZER -------------------- #
class SettingGroupSerializer(serializers.ModelSerializer):
    fields = serializers.SerializerMethodField()

    class Meta:
        model = SettingGroup
        fields = [
            "id",
            "name",
            "key",
            "icon",
            "description",
            "order",
            "is_active",
            "fields",
        ]

    def get_fields(self, obj):
        active_fields = obj.fields.filter(is_active=True).order_by("order", "label")

        return SettingFieldSerializer(
            active_fields,
            many=True,
            context=self.context,
        ).data


# -------------------- SETTING LEVEL SERIALIZER -------------------- #
class SettingLevelSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = SettingLevel
        fields = [
            "id",
            "name",
            "key",
            "order",
            "is_active",
            "groups",
        ]

    def get_groups(self, obj):
        active_groups = obj.groups.filter(is_active=True).order_by("order", "name")

        return SettingGroupSerializer(
            active_groups,
            many=True,
            context=self.context,
        ).data


# -------------------- SETTING UPDATE SERIALIZER -------------------- #
class SettingUpdateSerializer(serializers.Serializer):
    settings = serializers.DictField(required=True)

    def validate_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Settings must be an object.")

        return value