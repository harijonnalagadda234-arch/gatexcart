from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, QuoteRequest, HeroBanner

@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email")

@admin.register(QuoteRequest)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "email", "product", "status", "created_at")
    list_filter = ("status", "country")
    list_editable = ("status",)
    search_fields = ("name", "company", "email", "product")

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "preview", "is_active", "display_order", "created_at")
    list_editable = ("is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")
    readonly_fields = ("preview", "created_at")
    fields = ("title", "subtitle", "image", "preview", "button_text", "button_url", "is_active", "display_order", "created_at")

    @admin.display(description="Image preview")
    def preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:240px;height:68px;object-fit:cover;border:1px solid #ccd6e0;border-radius:5px;" />', obj.image.url)
        return "No image uploaded"
