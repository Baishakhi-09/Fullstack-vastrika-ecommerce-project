from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from apps.core import audit_signals
        from apps.core.audit_signals import register_audit_model
        from apps.orders.models import Order, Payment, Refund, Invoice

        register_audit_model(Order)
        register_audit_model(Payment)
        register_audit_model(Refund)
        register_audit_model(Invoice)