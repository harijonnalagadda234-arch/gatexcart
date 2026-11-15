from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about-us/", views.about, name="about"),
    path("industries-we-serve/", views.industries, name="industries"),
    path("how-it-works/", views.static_page, {"slug": "how"}, name="how"),
    path("resources/", views.static_page, {"slug": "resources"}, name="resources"),
    path("track-order/", views.static_page, {"slug": "track"}, name="track_order"),
    path("privacy-policy/", views.static_page, {"slug": "privacy"}, name="privacy"),
    path("terms-and-conditions/", views.static_page, {"slug": "terms"}, name="terms"),
    path("returns-and-refunds/", views.static_page, {"slug": "returns"}, name="returns"),
    path("cookie-policy/", views.static_page, {"slug": "cookies"}, name="cookies"),
    path("contact-us/", views.contact, name="contact"),
    path("request-a-quote/", views.quote, name="quote"),
]
