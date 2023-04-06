from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from main.models import Contact


class ContactView(CreateView):
    model = Contact
    template_name = "contact.html"
    fields = ['name', 'telephone', 'email', 'body']
    success_url = "/success?msg=Successfully submitted contact request."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ContactView, self).form_valid(form)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "register.html"
    success_url = "/success?msg=Thanks for registering"
