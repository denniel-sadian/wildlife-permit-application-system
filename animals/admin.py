from django.contrib import admin

from .models import Species, SubSpecies


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    '''Admin View for species.'''

    list_display = ('name', 'type')


@admin.register(SubSpecies)
class SubSpeciesAdmin(admin.ModelAdmin):
    '''Admin View for sub species.'''

    list_display = ('common_name', 'scientific_name',
                    'main_species', 'population')
    list_filter = ('main_species',)
    search_fields = ('common_name', 'scientific_name', 'main_species__name')
    ordering = ('common_name',)
