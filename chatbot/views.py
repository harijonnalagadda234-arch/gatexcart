import json
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils.html import strip_tags
from django.db.models import Q
from .models import ChatMessage
from catalog.models import Category, Product
from core.models import QuoteRequest


STOP_WORDS = {
    "a", "an", "and", "are", "can", "find", "for", "help", "i", "in", "is",
    "me", "of", "our", "please", "product", "products", "the", "to", "we",
    "what", "with", "you",
}


def build_reply(text):
    normalized = text.lower()

    if any(word in normalized for word in ("quote", "quotation", "price", "pricing", "bulk", "minimum order", "moq")):
        return (
            "To request pricing, share the product, required quantity and destination country "
            "using our quotation form: /request-a-quote/. Our team will follow up with availability and options."
        )

    terms = [term for term in re.findall(r"[a-z0-9]+", normalized) if len(term) > 2 and term not in STOP_WORDS]
    products = Product.objects.filter(is_active=True)
    if terms:
        product_query = Q()
        category_query = Q()
        for term in terms[:6]:
            product_query |= Q(name__icontains=term) | Q(short_description__icontains=term)
            category_query |= Q(name__icontains=term)
        matches = list(products.filter(product_query | Q(category__in=Category.objects.filter(category_query))).select_related("category").distinct()[:4])
        if matches:
            results = ", ".join(f"{product.name} ({product.category.name})" for product in matches)
            return f"These listed products may match your search: {results}. For pack sizes and bulk availability, request a quote at /request-a-quote/."

        categories = list(Category.objects.filter(is_active=True, name__icontains=terms[0])[:3])
        if categories:
            names = ", ".join(category.name for category in categories)
            return f"We work with the {names} category. Tell us your destination and quantity at /request-a-quote/ and our team can help check sourcing options."

    return (
        "Welcome to GateXKart. I can help you explore Indian food product categories or request a bulk quotation. "
        "Share a product name, or contact info@gatexkart.com / +91 98765 43210."
    )


def continue_quote_enquiry(request, text):
    enquiry = request.session.get("chat_enquiry")
    normalized = text.lower()

    if normalized in {"cancel", "cancel enquiry", "stop"}:
        request.session.pop("chat_enquiry", None)
        return "I cancelled that quotation enquiry. You can start again whenever you are ready."

    if not enquiry and any(word in normalized for word in ("quote", "quotation", "price", "pricing", "bulk", "minimum order", "moq")):
        request.session["chat_enquiry"] = {"step": "product", "answers": {}}
        return "I can send a quotation enquiry to our team. Which product are you looking for?"

    if not enquiry:
        return None

    step = enquiry["step"]
    answers = enquiry["answers"]
    prompts = {
        "product": ("product", 180, "What quantity do you need?"),
        "quantity": ("quantity", 100, "Which country should the order be delivered to?"),
        "country": ("country", 100, "What name should we use to follow up?"),
        "name": ("name", 150, "What email address can our team use to contact you?"),
    }

    if step in prompts:
        field, max_length, next_prompt = prompts[step]
        value = text.strip()
        if len(value) > max_length:
            return f"Please enter a shorter {field} (up to {max_length} characters)."
        answers[field] = value
        next_step = {"product": "quantity", "quantity": "country", "country": "name", "name": "email"}[step]
        request.session["chat_enquiry"] = {"step": next_step, "answers": answers}
        return next_prompt

    if step == "email":
        try:
            validate_email(text)
        except ValidationError:
            return "That email address does not look valid. Please enter it again, or type “cancel” to stop."
        answers["email"] = text.strip()
        request.session["chat_enquiry"] = {"step": "phone", "answers": answers}
        return "What phone number should our team use to follow up?"

    if step == "phone":
        phone = text.strip()
        if len(phone) > 30 or len(re.sub(r"\D", "", phone)) < 7:
            return "Please enter a phone number with at least 7 digits, or type “cancel” to stop."
        QuoteRequest.objects.create(
            name=answers["name"],
            email=answers["email"],
            phone=phone,
            country=answers["country"],
            product=answers["product"],
            quantity=answers["quantity"],
            message="Submitted via the GateXKart website assistant.",
        )
        request.session.pop("chat_enquiry", None)
        return "Thank you. Your quotation enquiry has been sent to our team. We will follow up using the contact details you provided."

    request.session.pop("chat_enquiry", None)
    return "I couldn't continue that quotation request. Please start again or use the Request a Quote form."


@require_POST
@csrf_protect
def message(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid message"}, status=400)
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
        return JsonResponse({"error": "Enter a message"}, status=400)

    text = strip_tags(payload["message"]).strip()[:1200]
    if not text:
        return JsonResponse({"error": "Enter a message"}, status=400)

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    ChatMessage.objects.create(session_key=session_key, role="user", message=text)
    answer = continue_quote_enquiry(request, text) or build_reply(text)
    ChatMessage.objects.create(session_key=session_key, role="assistant", message=answer)
    return JsonResponse({"reply": answer})
