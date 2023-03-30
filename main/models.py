from django.contrib.auth.models import User
from django.db import models


class Contact(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField()
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    index = models.IntegerField(default=0)
    deleted = models.BooleanField()