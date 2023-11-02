import base64
import calendar
import datetime
import json
from typing import Any

from django.views.generic import TemplateView
from django.db.models import Sum, F

from users.views import CustomLoginRequiredMixin
from users.models import Client

from permits.models import (
    TransportEntry,
    Status
)

from .models import Species


class TransportStatsView(CustomLoginRequiredMixin, TemplateView):
    template_name = 'animals/transport_stats.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tab'] = 'transport_stats'

        selected_year = int(self.request.GET.get(
            'year', datetime.datetime.now().year))
        context['year'] = selected_year
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
