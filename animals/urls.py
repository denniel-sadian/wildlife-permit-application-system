from django.urls import path

from . import views


urlpatterns = [
    # Autocomplete
    path('species/transport_stats/', views.TransportStatsView.as_view(),
         name='transport_stats'),
]
