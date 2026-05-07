from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .audit_middleware import get_current_user
from .models import AuditLog


AUDITED_MODELS = set()

IGNORE_FIELDS = {"updated_at", "created_at"}


def register_audit_model(model):
    AUDITED_MODELS.add(model)


@receiver(pre_save)
def store_old_values(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS or not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    changes = {}

    for field in sender._meta.fields:
        field_name = field.name

        if field_name in IGNORE_FIELDS:
            continue

        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(instance, field_name, None)

        if old_value != new_value:
            changes[field_name] = {
                "old": str(old_value)[:500],
                "new": str(new_value)[:500],
            }

    instance._audit_changes = changes


@receiver(post_save)
def create_audit_log(sender, instance, created, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    action = AuditLog.Action.CREATED if created else AuditLog.Action.UPDATED
    changes = {} if created else getattr(instance, "_audit_changes", {})

    if not created and not changes:
        return

    model_name = sender._meta.label

    AuditLog.objects.create(
        actor=get_current_user(),
        action=action,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=instance.pk,
        object_repr=f"{model_name} - {str(instance)}",
        changes=changes,
    )


@receiver(post_delete)
def create_delete_audit_log(sender, instance, **kwargs):

    if sender not in AUDITED_MODELS:
        return
    
    model_name = sender._meta.label

    AuditLog.objects.create(
        actor=get_current_user(),
        action=AuditLog.Action.DELETED,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=instance.pk,
        object_repr=f"{model_name} - {str(instance)}",
        changes={},
    )