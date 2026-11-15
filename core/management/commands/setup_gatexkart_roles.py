from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Category, Product
from core.models import HeroBanner, QuoteRequest, ContactMessage

class Command(BaseCommand):
    help = "Create the restricted GateXKart Admin group with catalogue, banner and enquiry permissions."

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="GateXKart Admin")
        models = [Category, Product, HeroBanner, QuoteRequest, ContactMessage]
        permissions = []
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            permissions.extend(Permission.objects.filter(content_type=ct))
        group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS(
            "GateXKart Admin group is ready. Assign staff users to this group in Django Admin."
        ))
