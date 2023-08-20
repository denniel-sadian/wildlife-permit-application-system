from django.db import models

from model_utils.managers import InheritanceManager

from animals.models import SubSpecies


class Status(models.TextChoices):
    DRAFT = 'DRAFT', 'On Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    RETURNED = 'RETURNED', 'Returned'
    ACCEPTED = 'Accepted', 'Accepted'
    RELEASED = 'RELEASED', 'Released'
    EXPIRED = 'EXPIRED', 'Expired'


class PermitType(models.TextChoices):
    WFP = 'WFP', 'Wildlife Farm Permit'
    WCP = 'WCP', 'Wildlife Collector Permit'
    LTP = 'LTP', 'Local Transport Permit'


class Permit(models.Model):
    permit_no = models.CharField(max_length=255)
    status = models.CharField(choices=Status.choices, max_length=50)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    objects = InheritanceManager()


class WildlifeFarmPermit(Permit):

    class Meta:
        verbose_name = "Wildlife Farm Permit"


class WildlifeCollectorPermit(Permit):

    class Meta:
        verbose_name = "Wildlife Collector's Permit"


class PermittedToCollectAnimal(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='species_permitted')
    wcp = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='wcp_species')
    quantity = models.IntegerField()


class LocalTransportPermit(Permit):
    wfp = models.ForeignKey(
        WildlifeFarmPermit, on_delete=models.CASCADE, related_name='wfp_ltps')
    wcp = models.ForeignKey(
        WildlifeFarmPermit, on_delete=models.CASCADE, related_name='wcp_ltps')
    transport_location = models.CharField(max_length=255)
    transport_date = models.DateField()

    class Meta:
        verbose_name = "Local Transport Permit"


class TransportEntry(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='transportings')
    ltp = models.ForeignKey(
        LocalTransportPermit, on_delete=models.CASCADE, related_name='species_to_transport')
    quantity = models.IntegerField()
