from typing import Any
from datetime import datetime

from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.db import transaction
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from users.views import CustomLoginRequiredMixin
from users.models import Client
from .models import (
    PermitApplication,
    Status
)
from .forms import (
    PermitApplicationForm, PermitApplicationUpdateForm,
    RequirementFormSet, TransportEntryFormSet, CollectionEntryFormSet
)


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

        requirements = self.object.requirements.all()
        transport_entries = self.object.requested_species_to_transport.all().order_by(
            'sub_species__main_species')
        requested_species = self.object.requested_species.all().order_by(
            'sub_species__main_species', 'sub_species__common_name')

        if self.request.POST:
            context['requirements'] = RequirementFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix='reqs')
            context['transport_entries'] = TransportEntryFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix='transports')
            context['requested_species'] = CollectionEntryFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix='collection_entries')
        else:
            context['requirements'] = RequirementFormSet(
                instance=self.object, queryset=requirements, prefix='reqs')
            context['transport_entries'] = TransportEntryFormSet(
                instance=self.object, queryset=transport_entries, prefix='transports')
            context['requested_species'] = CollectionEntryFormSet(
                instance=self.object, queryset=requested_species, prefix='collection_entries')

        client: Client = self.request.user.subclass
        if client.current_wcp:
            context['allowed_species'] = client.current_wcp.allowed_species.all()

        context['needed_requirements'] = self.object.needed_requirements

        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data()

        requirements = context['requirements']
        transport_entries = context['transport_entries']
        requested_species = context['requested_species']

        with transaction.atomic():

            form.instance.client = self.request.user.subclass
            self.object = form.save()

            if requirements.is_valid():
                requirements.save()

            if transport_entries.is_valid():
                transport_entries.save()

            if requested_species.is_valid():
                requested_species.save()

        messages.success(
            self.request,
            'Permit application has been saved')
        return super().form_valid(form)


class PermitApplicationDeleteView(DeleteView):
    model = PermitApplication
    template_name = 'permits/confirm_delete_permit_application.html'
    success_url = reverse_lazy('list_applications')
