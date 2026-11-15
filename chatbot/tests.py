import json

from django.test import Client, TestCase

from core.models import QuoteRequest


class ChatbotTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get("/")
        self.csrf_token = self.client.cookies["csrftoken"].value

    def send_message(self, message):
        return self.client.post(
            "/assistant/message/",
            data=json.dumps({"message": message}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )

    def test_product_question_uses_catalogue_records(self):
        response = self.send_message("Do you have basmati?")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Premium Basmati Rice", response.json()["reply"])

    def test_chatbot_collects_and_submits_a_quote_request(self):
        self.send_message("I need a bulk quote")
        self.send_message("Premium Basmati Rice")
        self.send_message("2 tonnes")
        self.send_message("United Arab Emirates")
        self.send_message("Asha Buyer")
        self.send_message("asha@example.com")
        response = self.send_message("+971501234567")

        self.assertEqual(response.status_code, 200)
        self.assertIn("quotation enquiry has been sent", response.json()["reply"])
        self.assertEqual(QuoteRequest.objects.count(), 1)
        self.assertEqual(QuoteRequest.objects.get().country, "United Arab Emirates")

    def test_chatbot_requires_csrf_protection(self):
        response = self.client.post(
            "/assistant/message/",
            data=json.dumps({"message": "hello"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
