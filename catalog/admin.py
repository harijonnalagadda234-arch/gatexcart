from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "image_preview", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)
    fields = ("name", "slug", "description", "image", "image_preview", "is_active", "sort_order")
    @admin.display(description="Current image")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:150px;height:100px;object-fit:cover;border-radius:5px;" />', obj.image.url)
        return "No image uploaded"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image", "image_preview", "alt_text", "display_order")
    readonly_fields = ("image_preview",)

    @admin.display(description="Current image")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:120px;height:100px;object-fit:contain;border-radius:5px;" />', obj.image.url)
        return "No image uploaded"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "image_preview", "origin", "moq", "is_featured", "is_active", "display_order")
    list_filter = ("category", "is_featured", "is_active")
    list_editable = ("is_featured", "is_active", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)
    fields = ("category", "name", "slug", "short_description", "description", "origin", "grade", "pack_sizes", "moq", "availability", "lead_time", "image", "image_preview", "is_featured", "is_active", "display_order")
    search_fields = ("name", "description", "category__name")
    inlines = [ProductImageInline]

    @admin.display(description="Current image")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:150px;height:150px;object-fit:cover;border-radius:5px;" />', obj.image.url)
        return "No image uploaded"
