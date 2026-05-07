from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import format_html
from xhtml2pdf import pisa

from vastrika_backend.admin_site import admin_site
from apps.orders.models import Invoice


@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "invoice_number", "created_at", "download_pdf_button",)
    search_fields = ("invoice_number", "order__order_number", "order__id")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("order",)
    readonly_fields = ("invoice_number", "created_at", "invoice_preview",)
    fieldsets = (
        ("Invoice Info", {
            "fields": (
                "order",
                "invoice_number",
                "created_at",
            )
        }),

        ("Preview", {
            "fields": (
                "invoice_preview",
            )
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:invoice_id>/download-pdf/",
                self.admin_site.admin_view(self.download_pdf),
                name="orders_invoice_download_pdf",
            ),
        ]

        return custom_urls + urls
    
    def download_pdf_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Download PDF</a>',
            f"{obj.id}/download-pdf/",
        )
    
    download_pdf_button.short_description = "PDF"

    def download_pdf(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        html = render_to_string(
            "admin/orders/invoice_pdf.html",
            {"invoice": invoice},
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{invoice.invoice_number}.pdf"'
        )

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse("PDF generation failed", status=500)
        
        return response
    
    def invoice_preview(self, obj):
        if not obj.pk:
            return "Save invoice first to preview."
        
        return format_html(
            """
            <div style="border:1px solid #e5e7eb; padding:20px; border-radius:12px;">
                <h2 style="margin:0 0 10px;">Invoice {}</h2>
                <p><strong>Order:</strong> {}</p>
                <p><strong>Customer:</strong> {}</p>
                <p><strong>Total:</strong> ₹{}</p>
                <p><strong>Date:</strong> {}</p>
            </div>
            """,
            obj.invoice_number,
            obj.order.order_number,
            obj.order.user.email or obj.order.user.username,
            obj.order.total_amount,
            obj.created_at.strftime("%d %b %Y"),
        )
    
    invoice_preview.short_description = "Invoice Preview"