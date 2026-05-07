from django.db import models
from django.conf import settings
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PAID = "paid", "Paid"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        RETURN_REQUESTED = "return_requested", "Return Requested"
        RETURN_APPROVED = "return_approved", "Return Approved"
        RETURN_PICKED = "return_picked", "Return Picked"
        RETURNED = "returned", "Returned"
        REFUNDED = "refunded", "Refunded"

    ALLOWED_STATUS_TRANSITIONS = {
        Status.PENDING: [Status.CONFIRMED, Status.CANCELLED],
        Status.CONFIRMED: [Status.PAID, Status.CANCELLED],
        Status.PAID: [Status.PACKED, Status.CANCELLED],
        Status.PACKED: [Status.SHIPPED, Status.CANCELLED],
        Status.SHIPPED: [Status.OUT_FOR_DELIVERY],
        Status.OUT_FOR_DELIVERY: [Status.DELIVERED],
        Status.DELIVERED: [Status.RETURN_REQUESTED],
        Status.RETURN_REQUESTED: [Status.RETURN_APPROVED],
        Status.RETURN_APPROVED: [Status.RETURN_PICKED],
        Status.RETURN_PICKED: [Status.RETURNED],
        Status.RETURNED: [Status.REFUNDED],
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_number = models.CharField(max_length=30, unique=True, db_index=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    shipping_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default="India")

    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    paid_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    return_requested_at = models.DateTimeField(null=True, blank=True)
    return_approved_at = models.DateTimeField(null=True, blank=True)
    return_picked_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["placed_at"]),
        ]

    def calculate_totals(self):
        subtotal = Decimal("0.00")
        gst_amount = Decimal("0.00")

        for item in self.items.all():
            subtotal += item.subtotal
            gst_amount += item.gst_amount

        self.subtotal = subtotal
        self.gst_amount = gst_amount
        self.total_amount = (
            self.subtotal
            + self.gst_amount
            + self.shipping_charge
            - self.discount_amount
        )

    def clean(self):
        if not self.pk:
            return
        
        old_order = Order.objects.get(pk=self.pk)

        if old_order.status == self.status:
            return
        
        allowed_next_statuses = self.ALLOWED_STATUS_TRANSITIONS.get(
            old_order.status,
            [],
        )

        if self.status not in allowed_next_statuses:
            raise ValidationError(
                {
                    "status": (
                        f"Invalid status change: "
                        f"{old_order.get_status_display()} → {self.get_status_display()}"
                    )
                }
            )
        
    def save(self, *args, **kwargs):
        now = timezone.now()

        if self.status == self.Status.PAID and not self.paid_at:
            self.paid_at = now

        if self.status == self.Status.PACKED and not self.packed_at:
            self.packed_at = now

        if self.status == self.Status.SHIPPED and not self.shipped_at:
            self.shipped_at = now

        if self.status == self.Status.OUT_FOR_DELIVERY and not self.out_for_delivery_at:
            self.out_for_delivery_at = now

        if self.status == self.Status.DELIVERED and not self.delivered_at:
            self.delivered_at = now

        if self.status == self.Status.CANCELLED and not self.cancelled_at:
            self.cancelled_at = now

        if self.status == self.Status.RETURN_REQUESTED and not self.return_requested_at:
            self.return_requested_at = now

        if self.status == self.Status.RETURN_APPROVED and not self.return_approved_at:
            self.return_approved_at = now

        if self.status == self.Status.RETURN_PICKED and not self.return_picked_at:
            self.return_picked_at = now

        if self.status == self.Status.RETURNED and not self.returned_at:
            self.returned_at = now

        if self.status == self.Status.REFUNDED and not self.refunded_at:
            self.refunded_at = now

        self.full_clean()
        super().save(*args, **kwargs)

    def timeline_steps(self):
        return [
            {"key": "placed", "label": "Order Placed", "done": bool(self.placed_at), "time": self.placed_at},
            {"key": "paid", "label": "Paid", "done": bool(self.paid_at), "time": self.paid_at},
            {"key": "packed", "label": "Packed", "done": bool(self.packed_at), "time": self.packed_at},
            {"key": "shipped", "label": "Shipped", "done": bool(self.shipped_at), "time": self.shipped_at},
            {"key": "out_for_delivery", "label": "Out for Delivery", "done": bool(self.out_for_delivery_at), "time": self.out_for_delivery_at},
            {"key": "delivered", "label": "Delivered", "done": bool(self.delivered_at), "time": self.delivered_at},
        ]
    
    def return_timeline_steps(self):
        return [
            {"key": "return_requested", "label": "Return Requested", "done": bool(self.return_requested_at), "time": self.return_requested_at},
            {"key": "return_approved", "label": "Return Approved", "done": bool(self.return_approved_at), "time": self.return_approved_at},
            {"key": "return_picked", "label": "Return Picked", "done": bool(self.return_picked_at), "time": self.return_picked_at},
            {"key": "returned", "label": "Returned", "done": bool(self.returned_at), "time": self.returned_at},
            {"key": "refunded", "label": "Refunded", "done": bool(self.refunded_at), "time": self.refunded_at},
        ]

    def __str__(self):
        return self.order_number
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    def calculate_totals(self):
        self.subtotal = self.price * self.quantity
        self.gst_amount = self.subtotal * self.gst_rate / Decimal("100")
        self.total_price = self.subtotal + self.gst_amount

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

        self.order.calculate_totals()
        self.order.save(
            update_fields=[
                "subtotal",
                "gst_amount",
                "total_amount",
            ]
        )

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)

        order.calculate_totals()
        order.save(
            update_fields=[
                "subtotal",
                "gst_amount",
                "total_amount",
            ]
        )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class Method(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        UPI = "upi", "UPI"
        CARD = "card", "Card"
        NET_BANKING = "net_banking", "Net Banking"
        WALLET = "wallet", "Wallet"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    payment_method = models.CharField(
        max_length=30,
        choices=Method.choices,
        default=Method.COD,
        db_index=True,
    )

    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
    )

    reason = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.status == self.Status.COMPLETED and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"
        
class Invoice(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="invoice",
    )

    invoice_number = models.CharField(max_length=30, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["created_at"]),
        ]

    def generate_invoice_number(self):
        year = timezone.now().year
        count = Invoice.objects.filter(created_at__year=year).count() + 1
        return f"INV-{year}-{count:04d}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number