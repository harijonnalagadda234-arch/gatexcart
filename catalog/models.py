from django.db import models
from django.utils.text import slugify
from .image_utils import validate_jpeg_image, fit_and_reencode_jpeg

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True, validators=[validate_jpeg_image], help_text="JPG/JPEG only, max 10 MB. Automatically center-cropped to 600 × 400 px.")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.image and not self.image._committed:
            processed = fit_and_reencode_jpeg(self.image, (600, 400))
            if processed:
                self.image.save(processed.name, processed, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    origin = models.CharField(max_length=100, default="India")
    grade = models.CharField(max_length=100, blank=True)
    pack_sizes = models.CharField(max_length=200, blank=True)
    moq = models.CharField(max_length=100, blank=True)
    availability = models.CharField(max_length=100, default="Available on request")
    lead_time = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True, validators=[validate_jpeg_image], help_text="JPG/JPEG only, max 10 MB. Automatically center-cropped to 1200 × 1200 px.")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.image and not self.image._committed:
            processed = fit_and_reencode_jpeg(self.image, (1200, 1200))
            if processed:
                self.image.save(processed.name, processed, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-is_featured", "display_order", "name"]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="additional_images")
    image = models.ImageField(
        upload_to="products/additional/",
        validators=[validate_jpeg_image],
        help_text="JPG/JPEG only, max 10 MB.",
    )
    alt_text = models.CharField(max_length=180, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["product", "image"], name="unique_product_image_path"),
        ]

    def __str__(self):
        return self.alt_text or f"{self.product.name} image"
