from dal import autocomplete

from .models import (
    SubSpecies
)


class SubSpeciesAutocompleteView(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return SubSpecies.objects.none()

        qs = SubSpecies.objects.all()

        if self.q:
            qs = qs.filter(common_name__istartswith=self.q,
                           scientific__istartswith=self.q,
                           main_species__name__istartswith=self.q)

        return qs
