from typing import Any
from datetime import datetime
import base64
import json

from django.db.models.query import QuerySet
from django.db.models import Q
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
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from users.views import CustomLoginRequiredMixin
from users.models import Client, Validator

from .models import (
    PermitApplication,
    Status,
    UploadedRequirement,
    TransportEntry,
    CollectionEntry,
    CollectorOrTrapper,
    Permit,
    Validation
)
from .forms import (
    PermitApplicationForm,
    PermitApplicationUpdateForm,
    UploadedRequirementForm,
    TransportEntryForm,
    CollectionEntryForm,
    CollectorOrTrapperForm
)
from .filters import (
    PermitApplicationFilter,
    PermitFilter
)
from .signals import (
    application_submitted,
    application_unsubmitted,
    permit_validated
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
    context_object_name = 'applications'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'applications'
        context['filters'] = PermitApplicationFilter(
            self.request.GET, request=self.request)
        return context

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        filters = PermitApplicationFilter(
            self.request.GET, request=self.request, queryset=qs)
        return filters.qs.order_by('-id')


class PermitApplicationUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = PermitApplication
    form_class = PermitApplicationUpdateForm
    template_name = 'permits/update_application.html'
    last_edited_list = None

    def get_queryset(self):
        return super().get_queryset().filter(client=self.request.user)

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
            context['collectors_or_trappers'] = CollectorOrTrapperForm(
                self.request.POST, self.request.FILES,
                prefix='collectors_or_trappers')
            context['requirement'] = UploadedRequirementForm(
                self.request.POST, self.request.FILES, prefix='requirement')
        else:
            context['transport_entry'] = TransportEntryForm(
                prefix='transport_entry')
            context['requested_species'] = CollectionEntryForm(
                prefix='requested_species')
            context['collectors_or_trappers'] = CollectorOrTrapperForm(
                prefix='collectors_or_trappers')
            context['requirement'] = UploadedRequirementForm(
                prefix='requirement')

        context['needed_requirements'] = self.object.needed_requirements

        content_type = ContentType.objects.get_for_model(PermitApplication)
        context['logs'] = LogEntry.objects \
            .filter(
                content_type=content_type,
                object_id=self.object.id) \
            .exclude(Q(change_message='[]') | Q(change_message='')) \
            .order_by('-action_time')

        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data()

        transport_entry = context['transport_entry']
        requested_species = context['requested_species']
        collectors_or_trappers = context['collectors_or_trappers']
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

            collectors_or_trappers.instance.permit_application = self.object
            if collectors_or_trappers.is_valid():
                collectors_or_trappers.save()
                self.last_edited_list = collectors_or_trappers.prefix
            else:
                for field, error_list in collectors_or_trappers.errors.items():
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

        return super().form_valid(form)


class PermitApplicationDeleteView(DeleteView):
    model = PermitApplication
    template_name = 'permits/confirm_delete_permit_application.html'
    success_url = reverse_lazy('list_applications')

    def get_queryset(self):
        return super().get_queryset().filter(client=self.request.user)


class SubmitRedirectView(CustomLoginRequiredMixin, SingleObjectMixin, RedirectView):
    model = PermitApplication

    def get_queryset(self):
        return super().get_queryset().filter(client=self.request.user)

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        permit_application: PermitApplication = self.get_object(
            self.get_queryset())
        same_url = reverse_lazy('update_application', kwargs={
                                'pk': permit_application.id})

        if not permit_application.submittable:
            messages.warning(
                self.request,
                'Your permit application is incomplete.')
            return same_url

        permit_application.status = Status.SUBMITTED
        permit_application.save()

        application_submitted.send(
            sender=self.request.user, application=permit_application)

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

            application_unsubmitted.send(
                sender=self.request.user, application=permit_application)

        return same_url


class PermitDetailView(DetailView):
    model = Permit

    def get_queryset(self):
        if isinstance(self.request.user.subclass, Client):
            return super().get_queryset().filter(client=self.request.user)
        return super().get_queryset()

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


class PermitListView(CustomLoginRequiredMixin, ListView):
    model = Permit
    paginate_by = 10
    context_object_name = 'permits'
    template_name = 'permits/permit_list.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'permits'
        context['filters'] = PermitFilter(
            self.request.GET, request=self.request)
        return context

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        filters = PermitFilter(
            self.request.GET, request=self.request, queryset=qs)
        return filters.qs.order_by('-id')


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


class CollectorOrTrapperDeleteView(PermitApplicationItemDeleteView):
    model = CollectorOrTrapper
    item_list = 'collectors_or_trappers'


class ValidateRedirectView(CustomLoginRequiredMixin, SingleObjectMixin, RedirectView):
    model = Permit

    def get_object(self, queryset=None):
        if isinstance(self.request.user.subclass, Validator):
            try:
                data = json.loads(base64.urlsafe_b64decode(
                    self.request.GET['data']).decode('utf-8'))
                return Permit.objects.get(permit_no=data['permit_no'], or_no=data['or_no'])
            except (KeyError, Permit.DoesNotExist) as e:
                raise PermissionDenied('No permit found.') from e
        raise PermissionDenied('You are not a validator.')

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        permit: Permit = self.get_object()

        params = ''
        if not hasattr(permit, 'validation') and permit.current_status == Status.RELEASED:
            Validation.objects.create(
                permit=permit, validator=self.request.user)
            permit.status = Status.USED
            permit.save()
            params = '?'+urlencode({'validated': True})

            permit_validated.send(sender=self.request.user, permit=permit)

        return reverse_lazy(
            'permit_detail',
            kwargs={'pk': permit.id}) + params
