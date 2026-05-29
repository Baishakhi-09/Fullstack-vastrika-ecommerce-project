from django import forms

from .models import Product, Brand, ProductTag


# Product
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

        labels = {
            "name": "Product Name",
        }

        widgets = {
            "allow_backorders": forms.CheckboxInput(
                attrs={
                    "id": "id_allow_backorders"
                }
            ),
            
            "name": forms.TextInput(
                attrs={
                    "class": "admin-input",
                    "autocomplete": "off",
                }
            ),
        }

    BASE_INPUT_CLASS = "admin-input"
    TEXTAREA_CLASS = "admin-textarea"
    SELECT_CLASS = "admin-select"
    CHECKBOX_CLASS = "admin-checkbox"
    FILE_INPUT_CLASS = "admin-file-input"

    def get_widget_class(
        self,
        widget
    ) -> str:

        if isinstance(widget, forms.Textarea):
            return self.TEXTAREA_CLASS

        if isinstance(widget, forms.Select):
            return self.SELECT_CLASS

        if isinstance(widget, forms.CheckboxInput):
            return self.CHECKBOX_CLASS

        if isinstance(widget, forms.ClearableFileInput):
            return self.FILE_INPUT_CLASS

        return self.BASE_INPUT_CLASS

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            existing_classes = field.widget.attrs.get(
                "class",
                ""
            )

            css_classes = [existing_classes]

            # Widget class
            css_classes.append(
                self.get_widget_class(field.widget)
            )
            
            # Placeholder
            if not isinstance(
                field.widget,
                forms.CheckboxInput
            ):
                field.widget.attrs.setdefault(
                    "placeholder",
                    field.label
                )

            # Decimal fields
            if field_name in [
                "price",
                "compare_price",
            ]:
                field.widget.attrs[
                    "inputmode"
                ] = "decimal"

            # Disable autocomplete
            if field_name in [
                "slug",
                "price",
                "compare_price",
            ]:
                field.widget.attrs[
                    "autocomplete"
                ] = "off"

            # JS hooks
            field.widget.attrs.update({
                "data-field-type": (
                    field.__class__.__name__
                )
            })

            field.widget.attrs["class"] = " ".join(
                filter(None, css_classes)
            )

        # Autofocus
        if "name" in self.fields:
            self.fields["name"].widget.attrs[
                "autofocus"
            ] = True

        # Slug hooks
        if "slug" in self.fields:
            self.fields["slug"].widget.attrs.update({
                "data-slug-field": "true"
            })

# Brand
class BrandAdminForm(forms.ModelForm):
    class Meta:
        model = Brand

        fields = "__all__"

        widgets = {
            "meta_title": forms.TextInput(
                attrs={
                    "id": "id_meta_title",
                    "class": "vTextField",
                }
            ),

            "meta_description": forms.Textarea(
                attrs={
                    "id": "id_meta_description",
                    "class": "vLargeTextField",
                    "rows": 4,
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "autocomplete": "organization"
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "autocomplete": "off"
                }
            ),
        }

# Product-tag
class ProductTagAdminForm(forms.ModelForm):
    class Meta:
        model = ProductTag

        fields = "__all__"
        
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class":
                        "producttag-input",

                    "placeholder":
                        "Enter product tag name",

                    "autocomplete":
                        "off",
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "class":
                        "producttag-input",

                    "placeholder":
                        "auto-generated-slug",

                    "autocomplete":
                        "off",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class":
                        "producttag-textarea",

                    "id":
                        "id_description",

                    "placeholder":
                        "Write a short description...",

                    "rows":
                        5,

                    "autocomplete":
                        "off",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class":
                        "producttag-select",
                }
            ),

            "visibility": forms.Select(
                attrs={
                    "class":
                        "producttag-select",
                }
            ),

            "display_priority": forms.NumberInput(
                attrs={
                    "class":
                        "producttag-input",

                    "placeholder":
                        "0",
                }
            ),
        }