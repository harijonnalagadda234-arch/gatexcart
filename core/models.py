from django.db import models
from catalog.image_utils import validate_jpeg_image, fit_and_reencode_jpeg

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class QuoteRequest(models.Model):
    name = models.CharField(max_length=150)
    company = models.CharField(max_length=180, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=100, blank=True)
    product = models.CharField(max_length=180, blank=True)
    quantity = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("new","New"),("in_progress","In Progress"),("quoted","Quoted"),("closed","Closed")], default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Quote #{self.pk} - {self.name}"

class HeroBanner(models.Model):
    title = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="hero_banners/", validators=[validate_jpeg_image], help_text="JPG/JPEG only, max 10 MB. Automatically center-cropped to exactly 1600 × 450 px.")
    button_text = models.CharField(max_length=60, blank=True, default="Explore Products")
    button_url = models.CharField(max_length=300, blank=True, default="/products/")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            processed = fit_and_reencode_jpeg(self.image, (1600, 450))
            if processed:
                self.image.save(processed.name, processed, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Hero banner"
        verbose_name_plural = "Hero banners"
