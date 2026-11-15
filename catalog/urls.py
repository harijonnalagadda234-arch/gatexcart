from django.urls import path
from . import views
urlpatterns=[path("",views.listing,name="products"),path("<slug:slug>/",views.detail,name="product")]
