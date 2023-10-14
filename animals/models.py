from django.db import models


class Type(models.TextChoices):
    FAUNA = 'FAUNA', 'Fauna'
    FLORA = 'FLORA', 'Flora'


class Species(models.Model):

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=5, choices=Type.choices)

    def __str__(self):
        return str(self.name)


class SubSpecies(models.Model):
    main_species = models.ForeignKey(
        Species, on_delete=models.CASCADE, related_name='sub_species')
    input_code = models.CharField(max_length=10, unique=True)
    common_name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.main_species.name + ' - ' + self.common_name)
