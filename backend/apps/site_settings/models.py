from django.core.exceptions import ValidationError
from django.db import models


# -------------------- SETTING LEVEL -------------------- #
class SettingLevel(models.Model):
    name = models.CharField(max_length=100)
    key = models.SlugField(
        unique=True,
        blank=True,
        null=True,
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Setting Level"
        verbose_name_plural = "Setting Levels"

    def __str__(self):
        return self.name


# -------------------- SETTING GROUP -------------------- #
class SettingGroup(models.Model):
    level = models.ForeignKey(
        SettingLevel,
        on_delete=models.CASCADE,
        related_name="groups",
        blank=True,
        null=True,
    )

    name = models.CharField(max_length=100)
    key = models.SlugField(
        unique=True,
        blank=True,
        null=True,
    )

    icon = models.CharField(
        max_length=80,
        blank=True,
        help_text="Example: fa-solid fa-gear / bi bi-gear / settings",
    )
    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["level__order", "order", "name"]
        verbose_name = "Setting Group"
        verbose_name_plural = "Setting Groups"

    def __str__(self):
        return self.name


# -------------------- SETTING FIELD -------------------- #
class SettingField(models.Model):
    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        EMAIL = "email", "Email"
        NUMBER = "number", "Number"
        TEXTAREA = "textarea", "Textarea"
        SELECT = "select", "Select"
        TOGGLE = "toggle", "Toggle"
        FILE = "file", "File"
        COLOR = "color", "Color"
        PASSWORD = "password", "Password"

    group = models.ForeignKey(
        SettingGroup,
        on_delete=models.CASCADE,
        related_name="fields",
    )

    label = models.CharField(max_length=150)
    key = models.SlugField(
        max_length=150,
        help_text="Example: store_name, primary_color",
    )
    field_type = models.CharField(
        max_length=30,
        choices=FieldType.choices,
    )

    placeholder = models.CharField(max_length=255, blank=True)
    help_text = models.CharField(max_length=255, blank=True)

    default_value = models.TextField(blank=True)
    value = models.TextField(blank=True)

    options = models.JSONField(
        blank=True,
        null=True,
        help_text='For select field only. Example: [{"label":"India","value":"IN"}]',
    )

    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["group__level__order", "group__order", "order", "label"]
        verbose_name = "Setting Field"
        verbose_name_plural = "Setting Fields"
        constraints = [
            models.UniqueConstraint(
                fields=["group", "key"],
                name="unique_setting_field_key_per_group",
            )
        ]

    def __str__(self):
        return f"{self.group.name} - {self.label}"

    def clean(self):
        super().clean()

        if self.field_type == self.FieldType.SELECT:
            if not self.options or not isinstance(self.options, list):
                raise ValidationError({
                    "options": "Select field requires options as a list."
                })

            for option in self.options:
                if not isinstance(option, dict):
                    raise ValidationError({
                        "options": "Each option must be an object."
                    })

                if "label" not in option or "value" not in option:
                    raise ValidationError({
                        "options": "Each option must contain label and value."
                    })

        if self.field_type == self.FieldType.TOGGLE:
            allowed_values = ["true", "false", "1", "0", "yes", "no", ""]

            if str(self.default_value).lower() not in allowed_values:
                raise ValidationError({
                    "default_value": "Toggle default value must be true or false."
                })

            if str(self.value).lower() not in allowed_values:
                raise ValidationError({
                    "value": "Toggle value must be true or false."
                })

    def get_value(self):
        return self.value if self.value != "" else self.default_value


# -------------------- SETTING FILE -------------------- #
class SettingFile(models.Model):
    field = models.OneToOneField(
        SettingField,
        on_delete=models.CASCADE,
        related_name="uploaded_file",
        limit_choices_to={"field_type": SettingField.FieldType.FILE},
    )

    file = models.FileField(upload_to="site_settings/")
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Setting File"
        verbose_name_plural = "Setting Files"

    def __str__(self):
        return self.field.label

    def clean(self):
        super().clean()

        if self.field and self.field.field_type != SettingField.FieldType.FILE:
            raise ValidationError({
                "field": "Setting file can only be attached to file-type setting fields."
            })