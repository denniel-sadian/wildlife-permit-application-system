from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


def custom_global_vars(request):
    protocol = 'https' if settings.USE_HTTPS else 'http'
    domain = get_current_site(request)
    context = {
        'DOMAIN': f'{protocol}://{domain}'
    }
    return context
