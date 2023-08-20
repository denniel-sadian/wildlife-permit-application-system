import uuid

from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Client
from .models import RegistrationToken
from .forms import ClientRegistrationForm


class ClientRegistrationView(FormView):
    template_name = 'users/client_registration_form.html'
    form_class = ClientRegistrationForm
    success_url = reverse_lazy('client-registration')

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        client: Client = form.instance
        client.is_active = False
        client.set_password(form.instance.password)
        client.save()

        token = RegistrationToken(user=client, token=str(uuid.uuid4()))
        token.save()

        return super().form_valid(form)
