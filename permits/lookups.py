from ajax_select import register, LookupChannel

from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Requirement


@register('needed-requirements')
class SubSpeciesLookup(LookupChannel):
    model = Requirement

    def get_query(self, q, request):
        query = \
            Q(code__icontains=q) | \
            Q(label__icontains=q)
        qs = self.model.objects.filter(query).order_by('label')
        return qs

    def check_auth(self, request):
        if not request.user.is_authenticated:
            return PermissionDenied
