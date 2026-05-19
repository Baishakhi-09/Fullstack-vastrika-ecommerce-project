from __future__ import annotations

import logging

from django.contrib import admin
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import (
    get_object_or_404,
)
from django.template.loader import (
    render_to_string,
)
from django.urls import (
    path,
    reverse,
)
from django.utils.html import (
    format_html,
)

from weasyprint import HTML

from apps.orders.models import (
    Invoice,
)

from vastrika_backend.admin_site import (
    admin_site,
)


logger = logging.getLogger(__name__)


# =========================================================
# INVOICE ADMIN
# =========================================================
@admin.register(
    Invoice,
    site=admin_site,
)
class InvoiceAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "order",
        "invoice_number",
        "created_at",
        "download_pdf_button",
    )

    search_fields = (
        "invoice_number",
        "order__order_number",
        "order__id",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = (
        "created_at"
    )

    list_per_page = 50

    list_select_related = (
        "order",
    )

    list_display_links = (
        "id",
        "invoice_number",
    )

    autocomplete_fields = (
        "order",
    )

    readonly_fields = (
        "invoice_number",
        "created_at",
        "invoice_preview",
    )

    fieldsets = (
        (
            "Invoice Information",
            {
                "fields": (
                    "order",
                    "invoice_number",
                    "created_at",
                )
            },
        ),
        (
            "Invoice Preview",
            {
                "fields": (
                    "invoice_preview",
                )
            },
        ),
    )

    # CUSTOM URLS
    def get_urls(
        self,
    ):
        urls = super().get_urls()

        custom_urls = [
            path(
                (
                    "<int:invoice_id>/"
                    "download-pdf/"
                ),
                self.admin_site.admin_view(
                    self.download_pdf,
                ),
                name=(
                    "orders_invoice_download_pdf"
                ),
            ),
        ]

        return custom_urls + urls

    # PDF DOWNLOAD BUTTON
    @admin.display(
        description="PDF",
    )
    def download_pdf_button(
        self,
        obj: Invoice,
    ) -> str:

        download_url = reverse(
            (
                "admin:"
                "orders_invoice_download_pdf"
            ),
            args=[obj.id],
        )

        return format_html(
            """
            <a
                class="button"
                href="{}"
                target="_blank"
            >
                Download PDF
            </a>
            """,
            download_url,
        )

    # PDF GENERATION
    def download_pdf(
        self,
        request: HttpRequest,
        invoice_id: int,
    ) -> HttpResponse:
        invoice = get_object_or_404(
            Invoice.objects.select_related(
                "order",
                "order__user",
            ),
            id=invoice_id,
        )

        logger.info(
            (
                "Generating invoice PDF "
                "for invoice=%s"
            ),
            invoice.invoice_number,
        )

        html = render_to_string(
            (
                "admin/orders/"
                "invoice_pdf.html"
            ),
            {
                "invoice": invoice,
            },
            request=request,
        )

        try:
            pdf_file = HTML(
                string=html,
                base_url=(
                    request.build_absolute_uri(
                        "/"
                    )
                ),
            ).write_pdf()

            response = HttpResponse(
                pdf_file,
                content_type=(
                    "application/pdf"
                ),
            )

            response[
                "Content-Disposition"
            ] = (
                "attachment; "
                f'filename="{invoice.invoice_number}.pdf"'
            )

            logger.info(
                (
                    "Invoice PDF generated "
                    "successfully."
                )
            )

            return response

        except Exception as exc:
            logger.exception(
                (
                    "Invoice PDF generation "
                    "failed: %s"
                ),
                exc,
            )

            return HttpResponse(
                (
                    "Failed to generate "
                    "invoice PDF."
                ),
                status=500,
            )

    # INVOICE PREVIEW
    @admin.display(
        description="Invoice Preview",
    )
    def invoice_preview(
        self,
        obj: Invoice,
    ) -> str:

        if not obj.pk:

            return (
                "Save invoice first "
                "to preview."
            )

        customer = (
            obj.order.user.email
            or obj.order.user.username
        )

        return format_html(
            """
            <div
                style="
                    border:1px solid #e5e7eb;
                    padding:24px;
                    border-radius:14px;
                    background:#ffffff;
                    max-width:700px;
                "
            >
                <h2
                    style="
                        margin-bottom:16px;
                    "
                >
                    Invoice {}
                </h2>

                <table
                    style="
                        width:100%;
                        border-collapse:collapse;
                    "
                >
                    <tr>
                        <td>
                            <strong>Order</strong>
                        </td>
                        <td>{}</td>
                    </tr>

                    <tr>
                        <td>
                            <strong>Customer</strong>
                        </td>
                        <td>{}</td>
                    </tr>

                    <tr>
                        <td>
                            <strong>Total</strong>
                        </td>
                        <td>₹{}</td>
                    </tr>

                    <tr>
                        <td>
                            <strong>Date</strong>
                        </td>
                        <td>{}</td>
                    </tr>
                </table>
            </div>
            """,
            obj.invoice_number,
            obj.order.order_number,
            customer,
            obj.order.total_amount,
            obj.created_at.strftime(
                "%d %b %Y"
            ),
        )

    # PERMISSIONS
    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Invoice | None = None,
    ) -> bool:
        return False

    def has_view_permission(
        self,
        request: HttpRequest,
        obj: Invoice | None = None,
    ) -> bool:
        return bool(
            request.user.is_authenticated
            and request.user.is_staff
        )