from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order
from apps.products.notifications.models import AdminNotification
from apps.products.notifications.utils import broadcast_admin_notification


@receiver(pre_save, sender=Order)
def store_old_order_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    old_order = Order.objects.filter(pk=instance.pk).first()
    instance._old_status = old_order.status if old_order else None


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    notification = None

    if created:
        notification = AdminNotification.objects.create(
            title="New Order Placed",
            message=f"New order #{instance.order_number} has been placed.",
            notification_type=AdminNotification.Type.ORDER,
            url=f"/admin/orders/order/{instance.id}/change/",
        )
    
    else:
        old_status = getattr(instance, "_old_status", None)

        if old_status == instance.status:
            return

        status_messages = {
            Order.Status.PAID: "Payment received",
            Order.Status.PACKED: "Order packed",
            Order.Status.SHIPPED: "Order shipped",
            Order.Status.OUT_FOR_DELIVERY: "Order is out for delivery",
            Order.Status.DELIVERED: "Order delivered",
            Order.Status.CANCELLED: "Order cancelled",
            Order.Status.RETURN_REQUESTED: "Return requested",
            Order.Status.RETURN_APPROVED: "Return approved",
            Order.Status.RETURN_PICKED: "Return picked",
            Order.Status.RETURNED: "Order returned",
            Order.Status.REFUNDED: "Refund completed",
        }

        message = status_messages.get(instance.status)

        if message:
            notification = AdminNotification.objects.create(
                title=message,
                message=f"Order #{instance.order_number}: {message}.",
                notification_type=AdminNotification.Type.ORDER,
                url=f"/admin/orders/order/{instance.id}/change/",
            )   

    if notification:
        broadcast_admin_notification(notification)