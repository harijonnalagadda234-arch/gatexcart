from django.conf import settings

from catalog.models import Category


def site_settings(request):
    return {
        "site_phone": "+91 98765 43210",
        "site_email": "info@gatexkart.com",
        "site_address": "Dubai, UAE",
        "footer_phone": settings.SITE_FOOTER_PHONE,
        "footer_email": settings.SITE_FOOTER_EMAIL,
        "footer_address": settings.SITE_FOOTER_ADDRESS,
        "site_designer": settings.SITE_DESIGNER,
        "nav_categories": Category.objects.filter(is_active=True).order_by("sort_order", "name"),
    }
