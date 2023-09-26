from django.urls import path

from . import views


urlpatterns = [
    # Autocomplete
    path('subspecies-autocomplete/', views.SubSpeciesAutocompleteView.as_view(),
         name='subspecies-autocomplete'),
]
