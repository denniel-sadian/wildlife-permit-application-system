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
from django.utils.http import urlencode

from users.views import CustomLoginRequiredMixin
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
    CertificateOfWildlifeRegistration,
    Validation
)
from .forms import (
    PermitApplicationForm,
    PermitApplicationUpdateForm,
    UploadedRequirementForm,
    TransportEntryForm,
    CollectionEntryForm
)
from .filters import (
    PermitApplicationFilter
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


class PermitApplicationListView(CustomLoginRequiredMixin, ListView):
    model = PermitApplication
    paginate_by = 10
    context_object_name = 'applications'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'applications'
        filters = PermitApplicationFilter(
            self.request.GET, request=self.request)
        context['filters'] = filters
        return context

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        filters = PermitApplicationFilter(
            self.request.GET, request=self.request, queryset=qs)
        print('yasss', filters.qs)
        return filters.qs


class PermitApplicationUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = PermitApplication
    form_class = PermitApplicationUpdateForm
    template_name = 'permits/update_application.html'
    last_edited_list = None

    def get_success_url(self) -> str:
        return reverse_lazy(
            'update_application',
            kwargs={'pk': self.object.pk}
        ) + '' if not self.last_edited_list else '#'+self.last_edited_list

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['transport_entry'] = TransportEntryForm(
                self.request.POST, self.request.FILES, prefix='transport_entry')
            context['requested_species'] = CollectionEntryForm(
                self.request.POST, self.request.FILES,
                prefix='requested_species')
            context['requirement'] = UploadedRequirementForm(
                self.request.POST, self.request.FILES, prefix='requirement')
        else:
            context['transport_entry'] = TransportEntryForm(
                prefix='transport_entry')
            context['requested_species'] = CollectionEntryForm(
                prefix='requested_species')
            context['requirement'] = UploadedRequirementForm(
                prefix='requirement')

        context['needed_requirements'] = self.object.needed_requirements

        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data()

        transport_entry = context['transport_entry']
        requested_species = context['requested_species']
        requirement = context['requirement']

        with transaction.atomic():

            form.instance.client = self.request.user.subclass
            self.object = form.save()

            errors = []

            transport_entry.instance.permit_application = self.object
            if transport_entry.is_valid():
                transport_entry.save()
                self.last_edited_list = transport_entry.prefix
            else:
                for field, error_list in transport_entry.errors.items():
                    for error in error_list:
                        errors.append(error)

            requested_species.instance.permit_application = self.object
            if requested_species.is_valid():
                requested_species.save()
                self.last_edited_list = requested_species.prefix
            else:
                for field, error_list in requested_species.errors.items():
                    for error in error_list:
                        errors.append(error)

            requirement.instance.permit_application = self.object
            if requirement.is_valid():
                requirement.save()
                self.last_edited_list = requirement.prefix
            else:
                for field, error_list in requirement.errors.items():
                    for error in error_list:
                        errors.append(error)

        selected_errors = [
            error for error in errors if error != 'This field is required.']

        if selected_errors:
            for error in selected_errors:
                messages.warning(self.request, error)
        else:
            messages.success(
                self.request,
                'Permit application has been saved')

        return super().form_valid(form)


class PermitApplicationDeleteView(DeleteView):
    model = PermitApplication
    template_name = 'permits/confirm_delete_permit_application.html'
    success_url = reverse_lazy('list_applications')


class SubmitRedirectView(CustomLoginRequiredMixin, SingleObjectMixin, RedirectView):
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
        try:
            templates = {
                'LocalTransportPermit': 'permits/ltp.html'
            }
            return [templates[self.object.type]]
        except KeyError:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permit: Permit = self.get_object().subclass
        context['permit'] = permit

        if 'validated' in self.request.GET and permit.status == Status.USED:
            context['status'] = 'validated'
        elif permit.current_status == Status.EXPIRED:
            context['status'] = 'expired'
        elif permit.current_status == Status.USED:
            context['status'] = 'used'
        else:
            context['status'] = 'nothing'

        return context


class PermitListView(QueryParamFilterMixin, CustomLoginRequiredMixin, ListView):
    model = Permit
    paginate_by = 10
    context_object_name = 'permits'
    template_name = 'permits/permit_list.html'
    filter_fields = ['status', 'permit_type']

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'permits'
        return context

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


class PermitApplicationItemDeleteView(CustomLoginRequiredMixin, DeleteView):
    model = None
    current_permit_application = None
    item_list = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self.current_permit_application = obj.permit_application
        return obj

    def get_success_url(self):
        return reverse_lazy(
            'update_application',
            kwargs={'pk': self.current_permit_application.pk}
        ) + '#'+self.item_list

    def get(self, request, *args, **kwargs):
        self.get_object()
        return self.delete(request, *args, **kwargs)


class UploadedRequirementDeleteView(PermitApplicationItemDeleteView):
    model = UploadedRequirement
    item_list = 'requirement'


class TransportEntryDeleteView(PermitApplicationItemDeleteView):
    model = TransportEntry
    item_list = 'transport_entry'


class CollectionEntryDeleteView(PermitApplicationItemDeleteView):
    model = CollectionEntry
    item_list = 'requested_species'


class ValidateRedirectView(CustomLoginRequiredMixin, SingleObjectMixin, RedirectView):
    model = Permit

    def get_object(self, queryset=None):
        permit_no = self.request.GET['permit_no']
        or_no = self.request.GET['or_no']
        return Permit.objects.get(permit_no=permit_no, or_no=or_no)

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        permit: Permit = self.get_object()

        params = ''
        if not hasattr(permit, 'validation') and permit.current_status == Status.RELEASED:
            Validation.objects.create(
                permit=permit, validator=self.request.user)
            permit.status = Status.USED
            permit.save()
            params = '?'+urlencode({'validated': True})

        return reverse_lazy(
            'permit_detail',
            kwargs={'pk': permit.id}) + params
