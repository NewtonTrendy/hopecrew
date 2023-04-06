from django.contrib import admin

from chat.models import Message, Command, CommandInput, UserPing, Report

# Register your models here.
admin.site.register(Message)
admin.site.register(UserPing)
admin.site.register(Command)
admin.site.register(CommandInput)
admin.site.register(Report)
