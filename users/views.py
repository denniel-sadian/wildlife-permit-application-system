from typing import Any
import uuid
from django.http import HttpResponse

from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView

from .models import User, Client
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


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('home')

    def form_valid(self, form: Any) -> HttpResponse:
        super().form_valid(form)
        user: User = self.request.user
        user.is_initial_password_changed = True
        user.save()
        return super().form_valid(form)


class HomeView(TemplateView):
    template_name = "users/index.html"

    def get(self, request, *args, **kwargs):
        user: User = request.user
        if user.is_authenticated and not user.is_initial_password_changed:
            return redirect('password_change')
        return super().get(request, *args, **kwargs)
