from ajax_select import register, LookupChannel

from django.core.exceptions import PermissionDenied
from django.db.models import Q

from permits.models import Status

from .models import SubSpecies


class SubSpeciesLookupMixin:

    def format_item_display(self, item):
        img_url = item.image.url if item.image else '/static/img/no-img.jpg'
        return (
            f'''
            <div class="selected-species">
              <div>
                <img src={img_url}>
                <span>{item.main_species.name + ' / ' + item.scientific_name + ' / ' + item.common_name}</span>
              </div>
            </div>
            ''')


@register('subspecies')
class SubSpeciesLookup(SubSpeciesLookupMixin, LookupChannel):
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
class PermittedSubSpeciesLookup(SubSpeciesLookupMixin, LookupChannel):
    model = SubSpecies

    def get_query(self, q, request):
        client = request.user.subclass
        query =  \
            (Q(common_name__icontains=q)
             | Q(scientific_name__icontains=q)
             | Q(main_species__name__icontains=q))  \
            & (Q(species_permitted__wcp__client=client)
               & Q(species_permitted__wcp__status=Status.RELEASED))
        qs = self.model.objects.filter(query).order_by('common_name')
        return qs

    def check_auth(self, request):
        if not request.user.is_authenticated:
            return PermissionDenied
