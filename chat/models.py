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

    def __str__(self):
        return self.user.username + " at " + self.dt


class Command(models.Model):
    name = models.CharField(max_length=200)
    tag = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    inputs = models.ManyToManyField("CommandInput")
    function_code = models.TextField()
    level = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class CommandInput(models.Model):
    name = models.CharField(max_length=200)
    tag = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    regex = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Report(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    msg = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True)