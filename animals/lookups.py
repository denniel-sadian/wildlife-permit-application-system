from ajax_select import register, LookupChannel

from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import SubSpecies


@register('subspecies')
class SubSpeciesLookup(LookupChannel):
    model = SubSpecies

    def get_query(self, q, request):
        query = \
            Q(common_name__icontains=q) | \
            Q(scientific_name__icontains=q) | \
            Q(main_species__name__icontains=q)
        qs = self.model.objects.filter(query).order_by('common_name')
        return qs

    def check_auth(self, request):
        if not request.user.is_authenticated:
            return PermissionDenied


@register('permitted-subspecies')
class PermittedSubSpeciesLookup(LookupChannel):
    model = SubSpecies

    def get_query(self, q, request):
        client = request.user.subclass
        query = \
            (Q(common_name__icontains=q) |
             Q(scientific_name__icontains=q) |
             Q(main_species__name__icontains=q)) & \
            (Q(species_permitted__wcp__client=client))
        qs = self.model.objects.filter(query).order_by('common_name')
        return qs

    def check_auth(self, request):
        if not request.user.is_authenticated:
            return PermissionDenied
