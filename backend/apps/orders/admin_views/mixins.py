class RoleBasedOrderAdminMixin:
    admin_roles = ["admin"]
    manager_roles = ["admin", "manager"]
    editor_roles = ["admin", "manager", "editor"]

    editor_hidden_fields = (
        "total_amount",
        "paid_at",
        "refunded_at",
    )

    def get_user_role(self, request):
        if request.user.is_superuser:
            return "admin"
        return getattr(request.user, "role", "editor")

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and self.get_user_role(request) in self.editor_roles

    def has_add_permission(self, request):
        return request.user.is_active and self.get_user_role(request) in self.manager_roles

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and self.get_user_role(request) in self.manager_roles

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and self.get_user_role(request) in self.admin_roles
    
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))

        if self.get_user_role(request) == "editor":
            fields = [field for field in fields if field not in self.editor_hidden_fields]
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if self.get_user_role(request) == "manager":
            readonly += ["total_amount"]

        return tuple(readonly)