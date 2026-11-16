import json
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import Category, Product, ProductImage


class CataloguePageTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.addCleanup(self.media_directory.cleanup)
        override = override_settings(MEDIA_ROOT=self.media_directory.name)
        override.enable()
        self.addCleanup(override.disable)

    def make_jpeg(self, name):
        content = BytesIO()
        Image.new("RGB", (32, 24), color=(30, 80, 120)).save(content, format="JPEG")
        return SimpleUploadedFile(name, content.getvalue(), content_type="image/jpeg")

    def test_seeded_catalogue_is_database_backed(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.filter(is_active=True).count(), 14)
        self.assertContains(response, "Products for every")
        self.assertContains(response, "gatexkart-global-export-hero.jpg")
        self.assertEqual(response.context["products"].count(), 4)
        self.assertEqual(
            [category.slug for category in response.context["featured_categories"]],
            ["rice-grains", "pulses-dals", "spices-masalas", "seeds-nuts", "tamarind", "other-food-products"],
        )

    def test_product_search_and_category_filter(self):
        response = self.client.get(
            "/products/",
            {"q": "toor", "category": "pulses-dals"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toor Dal")
        self.assertNotContains(response, "Premium Basmati Rice")

    def test_product_detail_is_public(self):
        product = Product.objects.get(slug="premium-basmati-rice")

        response = self.client.get(f"/products/{product.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Premium Basmati Rice")
        self.assertContains(response, "Request a Quote")

    def test_product_images_render_on_listing_and_detail_pages(self):
        product = Product.objects.get(slug="toor-dal")
        product.image = self.make_jpeg("toor-dal.jpg")
        product.save()
        additional = ProductImage.objects.create(
            product=product,
            image=self.make_jpeg("toor-dal-side-view.jpg"),
            alt_text="Toor Dal additional view",
            display_order=1,
        )

        listing = self.client.get("/products/")
        detail = self.client.get(f"/products/{product.slug}/")

        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, product.image.url)
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, product.image.url)
        self.assertContains(detail, additional.image.url)
        self.assertContains(detail, "Toor Dal additional view")

    def test_blank_product_image_uses_a_product_specific_placeholder(self):
        response = self.client.get("/products/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'aria-label="Product image unavailable: Premium Basmati Rice"',
        )
        self.assertNotContains(response, "food-market.jpg")

    def test_missing_image_url_shows_product_specific_placeholder(self):
        product = Product.objects.get(slug="toor-dal")
        product.image = "products/missing-image.jpg"
        product.save()

        response = self.client.get("/products/")

        self.assertContains(response, product.image.url)
        self.assertContains(
            response,
            'aria-label="Product image unavailable: Toor Dal"',
        )
        self.assertContains(response, "this.nextElementSibling.hidden=false")
        self.assertNotContains(response, "food-market.jpg")

    def test_catalogue_media_is_configured_for_staticfiles_collection(self):
        media_file = (
            Path(settings.BASE_DIR)
            / "media"
            / "products"
            / "catalogue"
            / "dry-garlic-whole-img0160.jpg"
        )

        self.assertTrue(media_file.is_file())
        self.assertIn(
            ("media", Path(settings.BASE_DIR) / "media"),
            settings.STATICFILES_DIRS,
        )

    def test_vercel_rewrites_media_urls_to_collected_static_assets(self):
        config_path = Path(settings.BASE_DIR) / "vercel.json"
        with config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)

        self.assertEqual(
            config["rewrites"],
            [
                {
                    "source": "/media/:path*",
                    "destination": "/static/media/:path*",
                }
            ],
        )
