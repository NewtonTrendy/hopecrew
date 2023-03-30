from django.urls import path, include
from django.views.generic import TemplateView

from main import views

urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"),
         name="home"),
    path('success',
         TemplateView.as_view(template_name="success.html"),
         name="success"),
    path('failure',
         TemplateView.as_view(template_name="failure.html"),
         name="failure"),
    path('contact', views.ContactView.as_view(), name="contact"),
    path('register', views.RegisterView.as_view(), name="register"),
    path('', include("django.contrib.auth.urls")),
]
