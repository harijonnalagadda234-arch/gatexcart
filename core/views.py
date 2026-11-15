from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from catalog.models import Category, Product

from .forms import ContactForm, QuoteForm
from .models import HeroBanner


SOLUTION_CARDS = [
    {
        "title": "Wholesalers",
        "image": "images/industries/wholesalers.jpeg",
        "description": "Dependable bulk sourcing for growing trade networks.",
    },
    {
        "title": "Retailers",
        "image": "images/industries/retailers.jpeg",
        "description": "Consistent products and pack options for your shelves.",
    },
    {
        "title": "Supermarkets",
        "image": "images/industries/supermarkets.jpeg",
        "description": "A broad range of quality-checked Indian staples.",
    },
    {
        "title": "Hotels & Restaurants",
        "image": "images/industries/hotels-restaurants.jpeg",
        "description": "Reliable ingredients for busy professional kitchens.",
    },
    {
        "title": "Distributors",
        "image": "images/industries/distributors.jpeg",
        "description": "Flexible sourcing to support your distribution plan.",
    },
    {
        "title": "Foodservice Businesses",
        "image": "images/industries/foodservice.jpeg",
        "description": "Bulk supply tailored to your foodservice needs.",
    },
    {
        "title": "Food Processing Units",
        "image": "images/industries/food-processing.jpeg",
        "description": "Sourcing support for food processing and manufacturing requirements.",
    },
]
INDUSTRY_CARDS = [
    {
        "title": "Wholesalers",
        "image": "images/logistics.jpg",
        "description": "Source Indian food and agricultural products in bulk for your wholesale business.",
    },
    {
        "title": "Retailers",
        "image": "images/food-market.jpg",
        "description": "Find product varieties and pack options suited to your retail customers.",
    },
    {
        "title": "Supermarkets",
        "image": "images/grains.jpg",
        "description": "Explore a broad selection of staples and Indian food products for your shelves.",
    },
    {
        "title": "Hotels & Restaurants",
        "image": "images/restaurant.jpg",
        "description": "Discuss dependable ingredient sourcing for your menus and professional kitchens.",
    },
    {
        "title": "Distributors",
        "image": "images/export-port.jpg",
        "description": "Coordinate product sourcing around your distribution needs and target markets.",
    },
    {
        "title": "Foodservice Businesses",
        "image": "images/spices.jpg",
        "description": "Request bulk sourcing options for the ingredients your foodservice operation uses.",
    },
    {
        "title": "Food Processing Units",
        "image": "images/pulses.jpg",
        "description": "Source food and agricultural inputs for your processing requirements.",
    },
    {
        "title": "Institutions & Government",
        "image": "images/basmati-rice.jpg",
        "description": "Share institutional product and quantity requirements with our B2B team.",
    },
]
HOMEPAGE_CATEGORY_SLUGS = [
    "rice-grains",
    "pulses-dals",
    "spices-masalas",
    "seeds-nuts",
    "tamarind",
    "other-food-products",
    "beverages-dairy",
    "disposable-plates",
    "disposable-cups",
    "food-containers",
    "food-packaging",
    "takeaway-packaging",
    "paper-products",
    "other-disposables",
]
STATIC_PAGES = {
    "how": (
        "How It Works",
        "Share your product and destination requirements. Our team reviews sourcing options, prepares a quotation and coordinates the next steps with you.",
    ),
    "resources": (
        "Trade Resources",
        "Talk with our team for product information, sourcing guidance and export documentation support for your market.",
    ),
    "track": (
        "Track an Order",
        "For an update on a current order, contact your GateXKart representative or email info@gatexkart.com with your order reference.",
    ),
    "privacy": (
        "Privacy Policy",
        "Information submitted through GateXKart enquiry forms is used to respond to business requests. Before launch, review this notice with your team and publish a complete privacy policy for your business and operating regions.",
    ),
    "terms": (
        "Terms & Conditions",
        "Product availability, specifications and commercial terms are confirmed during quotation. Publish business-specific terms here before accepting orders.",
    ),
    "returns": (
        "Returns & Refund Policy",
        "For questions about an order, contact our team using the details in your quotation. Any return or refund arrangements are subject to the commercial terms agreed for that order.",
    ),
    "cookies": (
        "Cookie Policy",
        "This site uses essential Django session and security cookies to support forms and the website assistant. Review this notice against your production configuration before launch.",
    ),
}


def about(request):
    return render(request, "pages/about.html")


def industries(request):
    return render(request, "pages/industries.html", {"industries": INDUSTRY_CARDS})


def home(request):
    categories = Category.objects.filter(is_active=True).order_by("sort_order", "name")
    category_by_slug = {category.slug: category for category in categories}
    featured_categories = [
        category_by_slug[slug]
        for slug in HOMEPAGE_CATEGORY_SLUGS
        if slug in category_by_slug
    ]
    products = Product.objects.filter(
        is_active=True,
    ).exclude(image="").select_related("category").order_by("-is_featured", "display_order", "name")[:4]
    if not products:
        products = Product.objects.filter(
            is_active=True,
            is_featured=True,
        ).select_related("category").order_by("display_order", "name")[:4]
    hero_banners = HeroBanner.objects.filter(
        is_active=True,
    ).exclude(image="").order_by("display_order", "-created_at")
    return render(request, "pages/home.html", {
        "categories": categories,
        "featured_categories": featured_categories,
        "products": products,
        "solutions": SOLUTION_CARDS,
        "hero_banners": hero_banners,
    })


def static_page(request, slug):
    page = STATIC_PAGES.get(slug)
    if page is None:
        raise Http404("Page not found.")
    title, body = page
    return render(request, "pages/info.html", {"title": title, "body": body})


def contact(request):
    form_data = request.POST if request.method == "POST" else None
    form = ContactForm(form_data)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thank you. Your message has been sent to our team.")
        return redirect("contact")
    return render(request, "pages/contact.html", {"form": form})


def quote(request):
    form_data = request.POST if request.method == "POST" else None
    form = QuoteForm(
        form_data,
        initial={"product": request.GET.get("product", "")},
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your quotation request has been received. Our team will be in touch.")
        return redirect("quote")
    return render(request, "pages/form.html", {"form": form, "title": "Request a Quote"})
