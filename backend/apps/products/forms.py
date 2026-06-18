from django import forms

from .models import(
    Product, 
    Brand, 
    ProductTag,
    ParentCategory,
    SubCategory,
    ChildCategory,
    ProductVariant,
    Warehouse,
)


class BaseCategoryForm(forms.ModelForm):
    def clean_name(self) -> str:
        return (
            self.cleaned_data["name"]
            .strip()
        )

    def clean_slug(self) -> str:
        slug = self.cleaned_data.get(
            "slug",
            ""
        )

        return slug.strip().lower()

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

            "tax": forms.Select(
                attrs={
                    "class": "admin-select",
                }
            ),

            "video": forms.ClearableFileInput(
                attrs={
                    "accept": "video/mp4,video/webm"
                }
            ),

            "meta_description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "admin-textarea",
                    "maxlength": 500,
                    "placeholder": "Meta description",
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
                (
                    forms.CheckboxInput,
                    forms.Select,
                    forms.ClearableFileInput,
                )
            ):
                field.widget.attrs.setdefault(
                    "placeholder",
                    field.label
                )

            # Decimal fields
            if field_name in [
                "mrp",
                "selling_price",
                "cost_price",
            ]:
                field.widget.attrs[
                    "inputmode"
                ] = "decimal"

            # Disable autocomplete
            if field_name in [
                "slug",
                "mrp",
                "selling_price",
                "cost_price",
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
                dict.fromkeys(
                    filter(None, css_classes)
                )
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

        if "child_category" in self.fields:
            self.fields[
                "child_category"
            ].queryset = (
                ChildCategory.objects
                .filter(is_active=True)
                .select_related(
                    "sub_category",
                    "sub_category__parent_category"
                )
            )

    def clean(self):
        cleaned_data = super().clean()

        mrp = cleaned_data.get("mrp")
        selling_price = cleaned_data.get("selling_price")

        if mrp is not None and mrp < 0:
            self.add_error(
                "mrp",
                "MRP cannot be negative."
            )

        if (
            selling_price is not None
            and selling_price < 0
        ):
            self.add_error(
                "selling_price",
                "Selling price cannot be negative."
            )

        if (
            mrp is not None
            and selling_price is not None
            and selling_price > mrp
        ):
            self.add_error(
                "selling_price",
                "Selling price cannot exceed MRP."
            )

        return cleaned_data

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

    def clean_name(self) -> str:
        return (
            self.cleaned_data["name"]
            .strip()
        )

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

    def clean_slug(self) -> str:
        slug = self.cleaned_data.get(
            "slug",
            ""
        )

        return slug.strip().lower()

    def clean_name(self) -> str:
        return self.cleaned_data[
            "name"
        ].strip()

# PARENT CATEGORY
class ParentCategoryForm(BaseCategoryForm):
    brands = forms.ModelMultipleChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=ProductTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = ParentCategory
        fields = "__all__"

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "saas-input",
                    "placeholder": "Enter category name",
                    "autocomplete": "off",
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "class": "saas-input",
                    "autocomplete": "off",
                }
            ),

            "short_description": forms.TextInput(
                attrs={
                    "class": "saas-input",
                    "maxlength": 255,
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "saas-textarea",
                    "rows": 5,
                }
            ),

            "meta_title": forms.TextInput(
                attrs={
                    "class": "saas-input",
                    "maxlength": 60,
                    "data-counter": "true",
                }
            ),

            "meta_description": forms.Textarea(
                attrs={
                    "class": "saas-textarea",
                    "rows": 4,
                    "maxlength": 160,
                    "data-counter": "true",
                }
            ),

            "seo_keywords": forms.TextInput(
                attrs={
                    "class": "saas-input",
                }
            ),

            "canonical_url": forms.URLInput(
                attrs={
                    "class": "saas-input",
                }
            ),

            "sort_order": forms.NumberInput(
                attrs={
                    "class": "saas-input",
                    "min": 0,
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "saas-file-input",
                }
            ),

            "banner": forms.ClearableFileInput(
                attrs={
                    "class": "saas-file-input",
                }
            ),

            "icon": forms.ClearableFileInput(
                attrs={
                    "class": "saas-file-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in ["brands", "tags"]:
            if field_name in self.fields:
                widget = self.fields[field_name].widget

                if hasattr(widget, "can_add_related"):
                    widget.can_add_related = False

                if hasattr(widget, "can_change_related"):
                    widget.can_change_related = False

                if hasattr(widget, "can_delete_related"):
                    widget.can_delete_related = False

                if hasattr(widget, "can_view_related"):
                    widget.can_view_related = False
    
    
class SubCategoryForm(BaseCategoryForm):
    class Meta:
        model = SubCategory

        fields = "__all__"

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(
            *args,
            **kwargs
        )

        for field_name, field in self.fields.items():
            existing_class = (
                field.widget.attrs.get(
                    "class",
                    ""
                )
            )

            field.widget.attrs.update({
                "autocomplete": "off",

                "class": (
                    f"{existing_class} form-control"
                ).strip()
            })

        if "name" in self.fields:
            self.fields["name"].widget.attrs.update({
                "placeholder":
                    "Enter sub category name"
            })

        if "slug" in self.fields:
            self.fields["slug"].widget.attrs.update({
                "placeholder":
                    "category-slug"
            })

        if "description" in self.fields:
            self.fields["description"].widget.attrs.update({
                "placeholder":
                    "Write a short description about this sub category",

                "rows": 5
            })

        if "sort_order" in self.fields:
            self.fields["sort_order"].widget.attrs.update({
                "placeholder":
                    "0"
            })

        if "parent_category" in self.fields:
            self.fields[
                "parent_category"
            ].label = "Parent Category"

        if "name" in self.fields:
            self.fields[
                "name"
            ].label = "Category Name"

        if "slug" in self.fields:
            self.fields[
                "slug"
            ].label = "URL Slug"

        if "description" in self.fields:
            self.fields[
                "description"
            ].label = "Description"

        if "sort_order" in self.fields:
            self.fields[
                "sort_order"
            ].label = "Sort Order"

class ChildCategoryForm(BaseCategoryForm):

    class Meta:
        model = ChildCategory

        fields = "__all__"

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "placeholder": "Enter child category name",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder":
                    "Write a short description"
                }
            ),

            "meta_title": forms.TextInput(
                attrs={
                    "maxlength": 60
                }
            ),

            "meta_description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": 160
                }
            ),
        }

class ProductVariantAdminForm(forms.ModelForm):

    class Meta:
        model = ProductVariant

        fields = (
            "product",
            "variant_name",
            "color",
            "size",
            "variant_sku",
            "barcode",
            "stock",
            "reserved_stock",
            "damaged_quantity",
            "is_active",
        )

class WarehouseAdminForm(forms.ModelForm):
    class Meta:

        model = Warehouse

        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if "name" in self.fields:
            self.fields["name"].widget.attrs.update({
                "autocomplete": "organization"
            })

        if "contact_person" in self.fields:
            self.fields["contact_person"].widget.attrs.update({
                "autocomplete": "name"
            })

        if "manager_name" in self.fields:
            self.fields["manager_name"].widget.attrs.update({
                "autocomplete": "name"
            })

        if "email" in self.fields:
            self.fields["email"].widget.attrs.update({
                "autocomplete": "email"
            })

        if "phone" in self.fields:
            self.fields["phone"].widget.attrs.update({
                "autocomplete": "tel"
            })

        if "location" in self.fields:
            self.fields["location"].widget.attrs.update({
                "autocomplete": "street-address"
            })