import uuid

from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Client
from .forms import ClientRegistrationForm
from .emails import RegistrationEmailView


class ClientRegistrationView(FormView):
    template_name = 'users/client_registration_form.html'
    form_class = ClientRegistrationForm
    success_url = reverse_lazy('client-registration')

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        client: Client = form.instance
        temporary_password = str(uuid.uuid4())
        client.set_password(temporary_password)
        client.save()

        RegistrationEmailView(client, temporary_password).send()

        return super().form_valid(form)
