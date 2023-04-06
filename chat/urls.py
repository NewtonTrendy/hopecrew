from django.urls import path
from django.views.generic import TemplateView, DetailView

from chat.models import Message
from chat.views import History, Edit, New, Chat, \
    Function, MessageMore, ReportView, EditView

urlpatterns = [
    path('', Chat.as_view(), name="chat"),
    path('message/<int:msg_id>', MessageMore.as_view(),
         name="chat_message_more"),
    path('message/report/<int:msg_pk>', ReportView.as_view(),
         name="chat_message_report"),
    path('message/edit/<int:pk>', EditView.as_view(),
         name="chat_message_edit"),
    path('api/new', New.as_view(), name="chat_new"),
    path('api/history', History.as_view(), name="chat_history"),
    path('api/edit', Edit.as_view(), name="chat_edit"),
    path('api/func/<str:tag>', Function.as_view(),
         name="chat_function")
]