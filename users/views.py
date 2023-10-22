from typing import Any

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import LoginView
from django.contrib import messages

from .models import User, Client
from .forms import ClientRegistrationForm

from .signals import user_created


class CustomLoginRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_initial_password_changed:
            return redirect('password_change')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'login'
        return context

    def get_default_redirect_url(self):
        super().get_default_redirect_url()
        if not self.request.user.is_initial_password_changed:
            return reverse_lazy('password_change')
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('home')


class ClientRegistrationView(FormView):
    template_name = 'users/registration.html'
    form_class = ClientRegistrationForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'register'
        return context

    def form_valid(self, form):
        '''If the form is valid, redirect to the supplied URL.'''
        user = form.instance
        user.save()
        user = User.objects.get(id=user.id)
        user_created.send_robust(sender=self.__class__, user=user)

        messages.info(
            self.request,
            "Your account registration is almost complete. "
            "An email is sent to your email containing your temporary password.")

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
    template_name = 'users/index.html'

    def get(self, request, *args, **kwargs):
        user: User = request.user
        if user.is_authenticated and not user.is_initial_password_changed:
            return redirect('password_change')

        return super().get(request, *args, **kwargs)


class ProfileView(CustomLoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'gender', 'phone_number',
              'title', 'signature_image')
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'profile'
        user = self.get_object()
        if user.type == Client.__name__:
            context['wfp'] = user.subclass.current_wfp
            context['wcp'] = user.subclass.current_wcp
        return context
