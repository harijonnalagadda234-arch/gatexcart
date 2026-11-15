from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

from .models import ContactMessage, QuoteRequest


class EnquiryFormTests(TestCase):
    def test_empty_quote_submission_reports_required_fields(self):
        response = self.client.post("/request-a-quote/", {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].errors["name"], ["This field is required."])

    def test_valid_quote_request_is_saved(self):
        response = self.client.post(
            "/request-a-quote/",
            {
                "name": "Asha Buyer",
                "company": "Example Trading",
                "email": "asha@example.com",
                "phone": "+971501234567",
                "country": "United Arab Emirates",
                "product": "Premium Basmati Rice",
                "quantity": "2 tonnes",
                "message": "Please share export pack options.",
            },
        )

        self.assertRedirects(response, "/request-a-quote/")
        self.assertEqual(QuoteRequest.objects.count(), 1)
        self.assertEqual(QuoteRequest.objects.get().product, "Premium Basmati Rice")

    def test_invalid_quote_email_is_rejected(self):
        response = self.client.post(
            "/request-a-quote/",
            {
                "name": "Asha Buyer",
                "email": "not-an-email",
                "phone": "+971501234567",
                "product": "Rice",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertContains(response, "Enter a valid email address")

    def test_contact_message_is_saved(self):
        response = self.client.post(
            "/contact-us/",
            {
                "name": "Asha Buyer",
                "email": "asha@example.com",
                "phone": "+971501234567",
                "subject": "Product question",
                "message": "Please contact me about your catalogue.",
            },
        )

        self.assertRedirects(response, "/contact-us/")
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_empty_contact_submission_reports_required_fields(self):
        response = self.client.post("/contact-us/", {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].errors["name"], ["This field is required."])


class MainNavigationAndIndustriesTests(TestCase):
    def test_homepage_industries_use_seven_distinct_uploaded_images(self):
        response = self.client.get("/")
        solutions = response.context["solutions"]
        expected_titles = [
            "Wholesalers",
            "Retailers",
            "Supermarkets",
            "Hotels & Restaurants",
            "Distributors",
            "Foodservice Businesses",
            "Food Processing Units",
        ]

        self.assertEqual([solution["title"] for solution in solutions], expected_titles)
        image_paths = [solution["image"] for solution in solutions]
        self.assertEqual(len(image_paths), 7)
        self.assertEqual(len(set(image_paths)), 7)
        for image_path in image_paths:
            with self.subTest(image=image_path):
                self.assertTrue((Path(settings.STATICFILES_DIRS[0]) / image_path).is_file())
                self.assertContains(response, f"/static/{image_path}")
        self.assertContains(response, "<h2 id=\"solutions-heading\">Industries We Serve</h2>")
        self.assertContains(response, "Flexible sourcing for buyers at every stage of the supply chain.")

    def test_internal_navigation_links_resolve_to_distinct_pages(self):
        routes = {
            "Home": ("/", "nav-home"),
            "About Us": ("/about-us/", "nav-about"),
            "Products": ("/products/", "nav-products"),
            "Industries We Serve": ("/industries-we-serve/", "nav-industries"),
            "How It Works": ("/how-it-works/", "nav-how"),
            "Resources": ("/resources/", "nav-resources"),
            "Contact Us": ("/contact-us/", "nav-contact"),
        }

        for label, (path, active_class) in routes.items():
            with self.subTest(label=label):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'href="{path}"')
                self.assertContains(response, f'class="{active_class} nav-active"')
                self.assertEqual(response.content.count(b'aria-current="page"'), 1)

    def test_industries_page_shows_its_own_active_navigation_item(self):
        response = self.client.get("/industries-we-serve/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a class="nav-industries nav-active" href="/industries-we-serve/" aria-current="page">Industries We Serve</a>')
        self.assertNotContains(response, '<a class="nav-home nav-active"')

    def test_industries_page_renders_all_business_cards_and_actions(self):
        response = self.client.get("/industries-we-serve/")

        self.assertEqual(response.status_code, 200)
        for title in (
            "Wholesalers",
            "Retailers",
            "Supermarkets",
            "Hotels &amp; Restaurants",
            "Distributors",
            "Foodservice Businesses",
            "Food Processing Units",
            "Institutions &amp; Government",
        ):
            with self.subTest(industry=title):
                self.assertContains(response, title)
        self.assertContains(response, 'href="/products/">Explore Products')
        self.assertContains(response, 'href="/request-a-quote/')


class AdminRoleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_gatexkart_roles", verbosity=0)
        cls.admin_group = Group.objects.get(name="GateXKart Admin")
        user_model = get_user_model()
        cls.restricted_admin = user_model.objects.create_user(
            username="catalogue-admin",
            password="test-password",
            is_staff=True,
        )
        cls.restricted_admin.groups.add(cls.admin_group)
        cls.superuser = user_model.objects.create_superuser(
            username="site-superuser",
            email="admin@example.com",
            password="test-password",
        )

    def test_restricted_admin_can_manage_catalogue_but_not_users(self):
        self.client.force_login(self.restricted_admin)

        self.assertEqual(self.client.get("/django-admin/catalog/product/").status_code, 200)
        self.assertEqual(self.client.get("/django-admin/auth/user/").status_code, 403)

    def test_superuser_has_full_admin_access(self):
        self.client.force_login(self.superuser)

        self.assertEqual(self.client.get("/django-admin/auth/user/").status_code, 200)

    def test_public_user_cannot_access_admin(self):
        response = self.client.get("/django-admin/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/django-admin/login/", response.url)
