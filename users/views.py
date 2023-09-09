import uuid

from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Client
from .forms import ClientRegistrationForm
from .emails import RegistrationEmailView


class ClientRegistrationView(FormView):
    template_name = 'users/registration.html'
    form_class = ClientRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        client: Client = form.instance
        temporary_password = str(uuid.uuid4())
        client.set_password(temporary_password)
        client.save()

        RegistrationEmailView(client, temporary_password).send()

        return super().form_valid(form)


class HomeView(TemplateView):
    template_name = "users/index.html"
