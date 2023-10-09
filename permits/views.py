from typing import Any
from datetime import datetime

from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.db import transaction
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import DeleteView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms

from users.views import CustomLoginRequiredMixin
from users.models import Client
from .models import (
    PermitApplication,
    PermitType,
    Status,
    UploadedRequirement,
    TransportEntry,
    CollectionEntry,
    Permit,
    LocalTransportPermit,
    WildlifeCollectorPermit,
    WildlifeFarmPermit,
    GratuitousPermit,
    CertificateOfWildlifeRegistration
)
from .forms import (
    PermitApplicationForm,
    PermitApplicationUpdateForm,
    UploadedRequirementForm,
    TransportEntryForm,
    CollectionEntryForm
)


class QueryParamFilterMixin:

    def get_query_filters(self):
        original_filters = {}
        for k, v in self.request.GET.items():
            if k.split('__')[0] in self.filter_fields:
                original_filters[k] = v

        modified_filters = {}
        for k, v in original_filters.items():
            if v == None or (v != None and v == 'ALL'):
                continue
            modified_filters[k] = v

        return original_filters, modified_filters

    def get_queryset(self) -> QuerySet[Any]:
        filters = self.get_query_filters()[1]

        queryset = self.model.objects.filter(
            client=self.request.user, **filters).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['permit_types'] = PermitType.choices
        context['statuses'] = Status.choices
        context.update(self.get_query_filters()[0])
        return context


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


class PermitApplicationListView(QueryParamFilterMixin, CustomLoginRequiredMixin, ListView):
    model = PermitApplication
    paginate_by = 10
    context_object_name = 'applications'
    filter_fields = ['permit_type', 'status']


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
        extra = 1 if self.object.editable else 0

        if self.request.POST:
            RequirementFormSet = forms.inlineformset_factory(
                PermitApplication, UploadedRequirement, form=UploadedRequirementForm, extra=extra)
            context['requirements'] = RequirementFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix='reqs')

            TransportEntryFormSet = forms.inlineformset_factory(
                PermitApplication, TransportEntry, form=TransportEntryForm, extra=extra)
            context['transport_entries'] = TransportEntryFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix='transports')

            CollectionEntryFormSet = forms.inlineformset_factory(
                PermitApplication, CollectionEntry, form=CollectionEntryForm, extra=extra)
            context['requested_species'] = CollectionEntryFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix='collection_entries')
        else:
            RequirementFormSet = forms.inlineformset_factory(
                PermitApplication, UploadedRequirement, form=UploadedRequirementForm, extra=extra)
            context['requirements'] = RequirementFormSet(
                instance=self.object, queryset=requirements, prefix='reqs')

            TransportEntryFormSet = forms.inlineformset_factory(
                PermitApplication, TransportEntry, form=TransportEntryForm, extra=extra)
            context['transport_entries'] = TransportEntryFormSet(
                instance=self.object, queryset=transport_entries, prefix='transports')

            CollectionEntryFormSet = forms.inlineformset_factory(
                PermitApplication, CollectionEntry, form=CollectionEntryForm, extra=extra)
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


class SubmitRedirectView(SingleObjectMixin, RedirectView):
    model = PermitApplication

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        permit_application: PermitApplication = self.get_object()
        same_url = reverse_lazy('update_application', kwargs={
                                'pk': permit_application.id})

        if not permit_application.submittable:
            messages.warning(
                self.request,
                'Your permit application is incomplete.')
            return same_url

        permit_application.status = Status.SUBMITTED
        permit_application.save()
        messages.success(
            self.request,
            f'Your permit application {permit_application.no} has been submitted. '
            'We have notified the admins already.')

        return same_url


class UnsubmitRedirectView(SingleObjectMixin, RedirectView):
    model = PermitApplication

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        permit_application: PermitApplication = self.get_object()
        same_url = reverse_lazy('update_application', kwargs={
                                'pk': permit_application.id})

        if permit_application.status == Status.SUBMITTED:
            permit_application.status = Status.DRAFT
            permit_application.save()

        return same_url


class PermitDetailView(DetailView):
    model = Permit

    def get_template_names(self) -> list[str]:
        templates = {
            'LocalTransportPermit': 'permits/ltp.html'
        }
        return [templates[self.object.type]]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permit'] = self.get_object().subclass
        return context


class PermitListView(QueryParamFilterMixin, CustomLoginRequiredMixin, ListView):
    model = Permit
    paginate_by = 10
    context_object_name = 'permits'
    template_name = 'permits/permit_list.html'
    filter_fields = ['status', 'permit_type']

    def get_queryset(self) -> QuerySet[Any]:
        filters = self.get_query_filters()[1]
        qs = None
        if 'permit_type' in filters:
            subclasses = {
                str(PermitType.LTP): LocalTransportPermit,
                str(PermitType.WFP): WildlifeFarmPermit,
                str(PermitType.WCP): WildlifeCollectorPermit,
                str(PermitType.CWR): CertificateOfWildlifeRegistration,
                str(PermitType.GP): GratuitousPermit
            }
            qs = subclasses[filters['permit_type']].objects
            del filters['permit_type']
        else:
            qs = self.model.objects

        return qs.filter(
            client=self.request.user, **filters).order_by('-created_at')
