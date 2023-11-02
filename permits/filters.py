import django_filters

from users.models import (
    Client
)

from .models import (
    PermitApplication,
    Permit,
    PermitType,
    LocalTransportPermit,
    WildlifeFarmPermit,
    WildlifeCollectorPermit,
    CertificateOfWildlifeRegistration,
    GratuitousPermit
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
        if user and isinstance(user.subclass, Client):
            return qs.filter(client=user.subclass)
        return qs.none()

    def search_filter(self, queryset, name, value):
        return queryset.filter(**{
            'no__icontains': value,
        })


class PermitFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        label='Search', method='search_filter')
    permit_type = django_filters.ChoiceFilter(
        label='Permit Type', choices=PermitType.choices,
        method='permit_type_filter')

    class Meta:
        model = Permit
        fields = ['permit_no', 'status']

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        subclasses = {
            PermitType.LTP: LocalTransportPermit,
            PermitType.WFP: WildlifeFarmPermit,
            PermitType.WCP: WildlifeCollectorPermit,
            PermitType.CWR: CertificateOfWildlifeRegistration,
            PermitType.GP: GratuitousPermit
        }
        if data and 'permit_type' in data and data['permit_type']:
            self.queryset = subclasses[data['permit_type']].objects

    @property
    def qs(self):
        qs = super().qs
        user = getattr(self.request, 'user', None)
        if user and isinstance(user.subclass, Client):
            return qs.filter(client=user.subclass)
        return qs

    def search_filter(self, queryset, name, value):
        return queryset.filter(**{
            'permit_no__icontains': value,
        })

    def permit_type_filter(self, queryset, name, value):
        return queryset
