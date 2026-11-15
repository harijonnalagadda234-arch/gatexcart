from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def listing(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    params = request.GET.copy()
    params.pop("page", None)
    page_obj = Paginator(products.order_by("-is_featured", "display_order", "name"), 24).get_page(
        request.GET.get("page")
    )
    return render(request, "catalog/list.html", {
        "products": page_obj,
        "page_obj": page_obj,
        "pagination_query": params.urlencode(),
        "categories": Category.objects.filter(is_active=True),
        "query": query,
        "selected_category": category_slug,
    })


def detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("additional_images"),
        slug=slug,
        is_active=True,
    )
    related_products = Product.objects.filter(
        is_active=True,
        category=product.category,
    ).exclude(pk=product.pk).order_by("-is_featured", "display_order", "name")[:4]
    return render(request, "catalog/detail.html", {
        "product": product,
        "related_products": related_products,
    })
