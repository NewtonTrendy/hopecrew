from django.urls import path
from django.views.generic import TemplateView

from chat.views import History, Edit, New, Chat

urlpatterns = [
    path('', Chat.as_view(), name="chat"),
    path('api/new', New.as_view(), name="chat_new"),
    path('api/history', History.as_view(), name="chat_history"),
    path('api/edit', Edit.as_view(), name="chat_edit"),
]