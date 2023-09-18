from typing import Any
from datetime import datetime

from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.db import transaction
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib import messages

from users.views import CustomLoginRequiredMixin
from .models import PermitApplication, Requirement, Status
from .forms import PermitApplicationForm, PermitApplicationUpdateForm, RequirementFormSet


class PermitApplicationCreateView(CustomLoginRequiredMixin, CreateView):
    model = PermitApplication
    form_class = PermitApplicationForm
    template_name = 'permits/create_application.html'
    success_url = reverse_lazy('list_applications')

    def get_success_url(self) -> str:
        return reverse_lazy('update_application', kwargs={'pk': self.object.pk})

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['client'] = self.request.user.subclass
        return initial

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        with transaction.atomic():
            self.object = form.save()
            self.object.status = Status.DRAFT
            current_date = datetime.now()
            formatted_date = current_date.strftime("%Y-%m")
            day_part = current_date.day
            no = f'PMDQ-{self.object.permit_type}-{formatted_date}-{day_part}-{self.object.id}'
            self.object.no = no
            self.object.save()

        messages.info(
            self.request,
            'Your new permit application has been created. You can now make further edits to it.')

        return super().form_valid(form)


class PermitApplicationListView(CustomLoginRequiredMixin, ListView):
    model = PermitApplication
    paginate_by = 10
    template_name = 'permits/list_applications.html'
    context_object_name = 'applications'

    def get_queryset(self) -> QuerySet[Any]:
        applications = PermitApplication.objects.filter(
            client=self.request.user).order_by('-created_at')
        return applications


class PermitApplicationUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = PermitApplication
    form_class = PermitApplicationUpdateForm
    template_name = 'permits/update_application.html'

    def get_success_url(self) -> str:
        return reverse_lazy('update_application', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        requirements = Requirement.objects.filter(
            permit_application=self.object)
        if self.request.POST:
            context['requirements'] = RequirementFormSet(
                self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['requirements'] = RequirementFormSet(
                instance=self.object, queryset=requirements)

        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data()
        requirements = context['requirements']
        with transaction.atomic():
            form.instance.client = self.request.user.subclass
            self.object = form.save()
            if requirements.is_valid():
                requirements.save()
            else:
                messages.info(
                    self.request,
                    'Application has been saved. But please make sure that once a requirement '
                    'is already submitted, you can no longer submit a double copy of it.')
                return super().form_valid(form)

        messages.success(
            self.request,
            'Permit application has been saved')
        return super().form_valid(form)
