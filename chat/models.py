from django.contrib.auth.models import User
import json
from django.db import models


class Message(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    msg_id = models.IntegerField()
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    edit_user = models.ForeignKey(User, on_delete=models.SET_NULL,
            default=None, blank=True, null=True, related_name="edit_user")
    index = models.IntegerField(default=0)
    edited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.body

class UserPing(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    dt = models.DateTimeField(auto_now_add=True)
