from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import CreateView, FormView
from main.models import Contact


class ContactView(CreateView):
    model = Contact
    template_name = "contact.html"
    fields = ['name', 'telephone', 'email', 'body']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ContactView, self).form_valid(form)


class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = "register.html"
    success_url = "/success?msg=Thanks for registering"
