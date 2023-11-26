from django.contrib import admin
from django.utils.html import mark_safe

from .models import Species, SubSpecies


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    '''Admin View for species.'''

    list_display = ('name', 'type')


@admin.register(SubSpecies)
class SubSpeciesAdmin(admin.ModelAdmin):
    '''Admin View for sub species.'''

    list_display = ('common_name', 'thumb', 'scientific_name',
                    'main_species', 'input_code')
    list_filter = ('main_species',)
    search_fields = ('input_code', 'common_name',
                     'scientific_name', 'main_species__name')
    ordering = ('common_name',)
    readonly_fields = ['image_preview']

    def thumb(self, obj):
        img_url = obj.image.url if obj.image else ''
        return mark_safe(f'<img src="{img_url}"  width="20" height="20"/>')

    thumb.allow_tags = True
    thumb.__name__ = 'Image'
