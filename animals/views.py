import base64
import calendar
import datetime
import json
from typing import Any
from urllib.parse import urlencode

from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, F

from users.views import CustomLoginRequiredMixin
from users.models import Client

from permits.models import (
    TransportEntry,
    Status
)
from permits.tasks import generate_reports

from .models import Species


def get_current_quarter():
    current_month = datetime.datetime.now().month
    if 1 <= current_month <= 3:
        return 1
    elif 4 <= current_month <= 6:
        return 2
    elif 7 <= current_month <= 9:
        return 3
    else:
        return 4


class TransportStatsView(CustomLoginRequiredMixin, TemplateView):
    template_name = 'animals/transport_stats.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'transport_stats'

        selected_year = int(self.request.GET.get(
            'year', datetime.datetime.now().year))
        selected_quarter = int(self.request.GET.get(
            'quarter', get_current_quarter()))
        context['year'] = selected_year
        context['quarter'] = selected_quarter
        data = {}
        for month in range(1, 13):
            from_date = f'{selected_year}-{month:02d}-01'
            to_date = f'{selected_year}-{month:02d}-{calendar.monthrange(selected_year, month)[1]}'

            for species in Species.objects.all():
                if species.name not in data:
                    data[species.name] = []

                filters = {
                    'ltp__status__in': [Status.RELEASED, Status.USED],
                    'ltp__transport_date__gte': from_date,
                    'ltp__transport_date__lte': to_date,
                    'sub_species__main_species': species
                }
                if isinstance(self.request.user.subclass, Client):
                    filters['ltp__client'] = self.request.user.subclass

                total = TransportEntry.objects \
                    .filter(**filters) \
                    .aggregate(total=Sum(F('quantity')))['total']
                data[species.name].append(total or 0)

        context['data'] = base64.urlsafe_b64encode(
            json.dumps(data).encode('utf-8')).decode('utf-8')

        return context


class GenerateReportsRedirectView(CustomLoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        self.generate_reports()
        messages.info(
            self.request,
            'Your reports are being generated and will be sent to your email. Please wait.')
        return reverse_lazy('transport_stats')+'?'+urlencode(self.request.GET)

    def generate_reports(self):
        generate_reports.delay(
            year=int(self.request.GET.get(
                'year', datetime.datetime.now().year)),
            quarter=int(self.request.GET.get(
                'quarter', get_current_quarter())),
            user_id=self.request.user.id
        )
