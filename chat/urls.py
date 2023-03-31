from django.urls import path
from django.views.generic import TemplateView

from chat.views import History, Edit, New

urlpatterns = [
    path('', TemplateView.as_view(template_name="chat.html"),
         name="chat_home"),
    path('api/new', New.as_view(), name="chat_new"),
    path('api/history', History.as_view(), name="chat_history"),
    path('api/edit', Edit.as_view(), name="chat_edit"),
]