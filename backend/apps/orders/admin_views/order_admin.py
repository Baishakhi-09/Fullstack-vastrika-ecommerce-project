from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.utils.html import format_html

from vastrika_backend.admin_site import admin_site
from apps.orders.models import Order
from apps.orders.audit_models import OrderActivityLog
from .mixins import RoleBasedOrderAdminMixin
from django.contrib.contenttypes.models import ContentType
from apps.core.models import AuditLog


@admin.register(Order, site=admin_site)
class OrderAdmin(RoleBasedOrderAdminMixin, admin.ModelAdmin):

    list_display = (
        "id",
        "order_number",
        "user",
        "status_badge",
        "total_amount",
        "placed_at",
        "quick_actions",
    )

    search_fields = (
        "order_number",
        "user__email",
        "user__username",
        "id",
    )

    list_filter = ("status", "placed_at")
    ordering = ("-placed_at",)
    list_select_related = ("user",)

    readonly_fields = (
        "placed_at",
        "updated_at",
        "paid_at",
        "packed_at",
        "shipped_at",
        "out_for_delivery_at",
        "delivered_at",
        "cancelled_at",
        "return_requested_at",
        "return_approved_at",
        "return_picked_at",
        "returned_at",
        "refunded_at",
        "order_tracking_timeline",
        "return_tracking_timeline",
        "activity_timeline",
        "audit_log_timeline",
    )

    fieldsets = (
        ("Order Info", {
            "fields": (
                "user",
                "order_number",
                "status",
                "total_amount",
            )
        }),
        ("Shipping Info", {
            "fields": (
                "shipping_name",
                "shipping_phone",
                "shipping_address",
                "shipping_city",
                "shipping_state",
                "shipping_pincode",
                "shipping_country",
            )
        }),

        ("Vastrika Tracking Timeline", {
            "fields": (
                "order_tracking_timeline",
                "return_tracking_timeline",
            )
        }),

        ("Activity Timeline", {
            "fields": (
                "activity_timeline",
            )
        }),

        ("System Timestamps", {
            "fields": (
                "placed_at",
                "updated_at",
                "paid_at",
                "packed_at",
                "shipped_at",
                "out_for_delivery_at",
                "delivered_at",
                "cancelled_at",
                "return_requested_at",
                "return_approved_at",
                "return_picked_at",
                "returned_at",
                "refunded_at",
                "audit_log_timeline",
            )
        }),
    )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path("<int:order_id>/mark-paid/", self.admin_site.admin_view(self.mark_paid), name="orders_order_mark_paid"),
            path("<int:order_id>/mark-packed/", self.admin_site.admin_view(self.mark_packed), name="orders_order_mark_packed"),
            path("<int:order_id>/mark-shipped/", self.admin_site.admin_view(self.mark_shipped), name="orders_order_mark_shipped"),
            path("<int:order_id>/out-for-delivery/", self.admin_site.admin_view(self.mark_out_for_delivery), name="orders_order_out_for_delivery"),
            path("<int:order_id>/mark-delivered/", self.admin_site.admin_view(self.mark_delivered), name="orders_order_mark_delivered"),
            path("<int:order_id>/request-return/", self.admin_site.admin_view(self.request_return), name="orders_order_request_return"),
            path("<int:order_id>/approve-return/", self.admin_site.admin_view(self.approve_return), name="orders_order_approve_return"),
            path("<int:order_id>/return-picked/", self.admin_site.admin_view(self.return_picked), name="orders_order_return_picked"),
            path("<int:order_id>/mark-returned/", self.admin_site.admin_view(self.mark_returned), name="orders_order_mark_returned"),
            path("<int:order_id>/mark-refunded/", self.admin_site.admin_view(self.mark_refunded), name="orders_order_mark_refunded"),
            path("<int:order_id>/cancel-order/", self.admin_site.admin_view(self.cancel_order), name="orders_order_cancel_order"),
        ]

        return custom_urls + urls
    
    def change_status(self, request, order_id, new_status, success_message):
        order = get_object_or_404(Order, id=order_id)
        old_status = order.status

        try:
            order.status = new_status
            order.save()

            OrderActivityLog.objects.create(
                order=order,
                actor=request.user if request.user.is_authenticated else None,
                action=OrderActivityLog.Action.STATUS_CHANGED,
                message=f"{request.user} changed status from {old_status} to {new_status}.",
                old_status=old_status,
                new_status=new_status,
            )

            messages.success(request, success_message)

        except ValidationError as exc:
            messages.error(
                request,
                exc.message_dict.get("status", ["Invalid status change."])[0]
            )

        except Exception:
            messages.error(request, "Something went wrong. Please try again.")

        return redirect(request.META.get("HTTP_REFERER", "../"))
    
    def activity_timeline(self, obj):
        logs = obj.activity_logs.select_related("actor").all()[:20]

        if not logs:
            return "No activity yet."
        
        html = """
        <div style="display:flex; flex-direction:column; gap:12px;">
        """

        for log in logs:
            actor = log.actor.email if log.actor and log.actor.email else "System"
            created = log.created_at.strftime("%d %b %Y, %I:%M %p")

            html += f"""
            <div style="
                border-left:3px solid #2563eb;
                padding-left:12px;
                background:#f9fafb;
                border-radius:8px;
                padding-top:8px;
                padding-bottom:8px;">

                <div style="font-weight:700; color:#111827;">{log.get_action_display()}</div>
                <div style="font-size:13px; color:#374151;">{log.message}</div>
                <div style="font-size:12px; color:#6b7280; margin-top:4px;">
                    By {actor} • {created}
                </div>
            </div>
            """
        html += "</div>"

        return format_html(html)
    activity_timeline.short_description = "Activity Timeline"
    
    def mark_paid(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.PAID, "Order marked as paid.")
    
    def mark_packed(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.PACKED, "Order marked as packed.")
    
    def mark_shipped(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.SHIPPED, "Order marked as shipped.")

    def mark_out_for_delivery(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.OUT_FOR_DELIVERY, "Order marked as out for delivery.")

    def mark_delivered(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.DELIVERED, "Order marked as delivered.")
    
    def request_return(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.RETURN_REQUESTED, "Return requested.")

    def approve_return(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.RETURN_APPROVED, "Return approved.")
    
    def return_picked(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.RETURN_PICKED, "Return picked.")

    def mark_returned(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.RETURNED, "Order marked as returned.")
    
    def mark_refunded(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.REFUNDED, "Order marked as refunded.")

    def cancel_order(self, request, order_id):
        return self.change_status(request, order_id, Order.Status.CANCELLED, "Order cancelled.")
    
    def audit_log_timeline(self, obj):
        if not obj.pk:
            return "Save order first to view audit logs."
        
        content_type = ContentType.objects.get_for_model(obj)

        logs = AuditLog.objects.filter(
            content_type=content_type,
            object_id=obj.pk,
        ).select_related("actor").order_by("-created_at")[:20]

        if not logs:
            return "No audit logs yet."
        
        html = """
        <div style="display:flex; flex-direction:column; gap:12px;">
        """

        for log in logs:
            actor = (
                log.actor.email
                if log.actor and log.actor.email
                else log.actor.username
                if log.actor
                else "System"
            )

            created = log.created_at.strftime("%d %b %Y, %I:%M %p")

            html += f"""
            <div style="
                border-left:4px solid #2563eb;
                background:#f9fafb;
                padding:12px 14px;
                border-radius:10px;">

                <div style="font-weight:800; color:#111827;">
                    {log.get_action_display()}
                </div>

                <div style="font-size:13px; color:#374151; margin-top:4px;">
                    {log.object_repr}
                </div>

                <div style="font-size:12px; color:#6b7280; margin-top:6px;">
                    By {actor} • {created}
                </div>
            </div>
            """
        html += "</div>"

        return format_html(html)
    
    audit_log_timeline.short_description = "Audit Logs"

    # ---------------- STATUS BADGE ---------------- #
    def status_badge(self, obj):
        styles = {
            "pending": ("Pending", "#f59e0b"),
            "confirmed": ("Confirmed", "#3b82f6"),
            "paid": ("Paid", "#2563eb"),
            "packed": ("Packed", "#8b5cf6"),
            "shipped": ("Shipped", "#6366f1"),
            "out_for_delivery": ("Out for Delivery", "#06b6d4"),
            "delivered": ("Delivered", "#16a34a"),
            "cancelled": ("Cancelled", "#dc2626"),
            "return_requested": ("Return Requested", "#f97316"),
            "return_approved": ("Return Approved", "#ea580c"),
            "return_picked": ("Return Picked", "#c2410c"),
            "returned": ("Returned", "#6b7280"),
            "refunded": ("Refunded", "#059669"),
        }

        label, color = styles.get(obj.status, ("Unknown", "#6b7280"))

        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:7px; '
            'background:{}; color:white; padding:5px 12px; border-radius:999px; '
            'font-size:12px; font-weight:700; box-shadow:0 2px 6px rgba(0,0,0,0.12);">'
            '<span style="width:7px; height:7px; border-radius:50%; background:white; display:inline-block;"></span>'
            '<span>{}</span></span>',
            color,
            label,
        )
    
    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    # ---------------- QUICK ACTIONS ---------------- #
    def quick_actions(self, obj):
        request = getattr(self, "_current_request", None)
        
        buttons = []

        # Admin + Manager
        if request and self.can_ship(request):
            buttons += [
                (f"{obj.id}/mark-packed/", "Pack"),
                (f"{obj.id}/mark-shipped/", "Ship"),
                (f"{obj.id}/out-for-delivery/", "OFD"),
                (f"{obj.id}/mark-delivered/", "Deliver"),
            ]

        # Admin + Manager
        if request and self.can_cancel(request):
            buttons.append((f"{obj.id}/cancel-order/", "Cancel"))

        # Admin only
        if request and self.can_refund(request):
            buttons += [
                (f"{obj.id}/approve-return/", "Approve Return"),
                (f"{obj.id}/mark-refunded/", "Refund"),
            ]
        
        html = '<div style="display:flex; flex-wrap:wrap; gap:6px; min-width:360px;">'

        for url, label in buttons:
            danger = 'style="color:#dc2626;"' if label == "Cancel" else ""
            html += f'<a class="button" {danger} href="{url}">{label}</a>'

        return format_html(
            """
            <div style="display:flex; flex-wrap:wrap; gap:6px; min-width:360px;">
                <a class="button" href="{}">Paid</a>
                <a class="button" href="{}">Pack</a>
                <a class="button" href="{}">Ship</a>
                <a class="button" href="{}">OFD</a>
                <a class="button" href="{}">Deliver</a>
                <a class="button" href="{}">Request Return</a>
                <a class="button" href="{}">Approve Return</a>
                <a class="button" href="{}">Return Picked</a>
                <a class="button" href="{}">Returned</a>
                <a class="button" href="{}">Refund</a>
                <a class="button" style="color:#dc2626;" href="{}">Cancel</a>
            </div>
            """,
            f"{obj.id}/mark-paid/",
            f"{obj.id}/mark-packed/",
            f"{obj.id}/mark-shipped/",
            f"{obj.id}/out-for-delivery/",
            f"{obj.id}/mark-delivered/",
            f"{obj.id}/request-return/",
            f"{obj.id}/approve-return/",
            f"{obj.id}/return-picked/",
            f"{obj.id}/mark-returned/",
            f"{obj.id}/mark-refunded/",
            f"{obj.id}/cancel-order/",
        )
    
    quick_actions.short_description = "Quick Actions"

    def order_tracking_timeline(self, obj):
        return self.render_progress_timeline(obj.timeline_steps())
    
    order_tracking_timeline.short_description = "Order Tracking"

    def return_tracking_timeline(self, obj):
        return self.render_progress_timeline(obj.return_timeline_steps())
    
    return_tracking_timeline.short_description = "Return Tracking"

    def changelist_view(self, request, extra_context=None):
        self._current_request = request
        return super().changelist_view(request, extra_context)
    
    def can_ship(self, request):
        return self.get_user_role(request) in ["admin", "manager"]
    
    def can_cancel(self, request):
        return self.get_user_role(request) in ["admin", "manager"]
    
    def can_refund(self, request):
        return self.get_user_role(request) == "admin"

    def render_progress_timeline(self, steps):
        if not steps:
            return "-"
        
        completed_count = sum(1 for step in steps if step["done"])
        total = len(steps)
        progress_percent = int((completed_count / total) * 100) if total else 0

        html = f"""
        <div style="padding:18px; border:1px solid #e5e7eb; border-radius:14px; background:#ffffff;">
            <div style="height:8px; background:#e5e7eb; border-radius:999px; overflow:hidden; margin-bottom:18px;">
                <div style="height:8px; width:{progress_percent}%; background:#16a34a;"></div>
            </div>

            <div style="display:grid; grid-template-columns:repeat({total}, 1fr); gap:8px;">
        """

        for step in steps:
            done = step["done"]
            color = "#16a34a" if done else "#d1d5db"
            label_color = "#111827" if done else "#6b7280"
            time_text = step["time"].strftime("%d %b %Y, %I:%M %p") if step["time"] else "Pending"

            html += f"""
                <div style="text-align:center;">
                    <div style="
                        width:22px;
                        height:22px;
                        border-radius:50%;
                        background:{color};
                        margin:0 auto 8px;
                        color:white;
                        font-size:13px;
                        font-weight:800;
                        line-height:22px;
                    ">{"✓" if done else ""}</div>

                    <div style="font-weight:700; color:{label_color}; font-size:12px;">
                        {step["label"]}
                    </div>

                    <div style="font-size:11px; color:#6b7280; margin-top:4px;">
                        {time_text}
                    </div>
                </div>
            """

        html += """
            </div>
        </div>
        """
            
        return format_html(html)