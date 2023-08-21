from django.db import models


class Type(models.TextChoices):
    FAUNA = 'FAUNA', 'Fauna'
    FLORA = 'FLORA', 'Flora'


class Species(models.Model):

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=5, choices=Type.choices)

    def __str__(self):
        return self.name


class SubSpecies(models.Model):
    main_species = models.ForeignKey(
        Species, on_delete=models.CASCADE, related_name='sub_species')
    common_name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255)
    population = models.IntegerField()
