from django.urls import path

from . import views


urlpatterns = [
    path('species/transport_stats/', views.TransportStatsView.as_view(),
         name='transport_stats'),
    path('species/generate_reports/', views.GenerateReportsRedirectView.as_view(),
         name='generate_reports'),
]
