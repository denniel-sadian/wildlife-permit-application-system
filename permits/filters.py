import django_filters

from users.models import (
    Client
)

from .models import (
    PermitApplication
)


class PermitApplicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        label='Search', method='search_filter')

    class Meta:
        model = PermitApplication
        fields = ['permit_type', 'status']

    @property
    def qs(self):
        qs = super().qs
        user = getattr(self.request, 'user', None)
        if user.type == Client.__name__:
            return qs.filter(client=user.subclass)
        return qs

    def search_filter(self, queryset, name, value):
        return queryset.filter(**{
            'no__icontains': value,
        })
