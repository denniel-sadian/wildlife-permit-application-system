from django.db import models

from model_utils.managers import InheritanceManager

from animals.models import SubSpecies
from users.models import Client, Permittee


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


class RequirementType(models.TextChoices):
    REQUIREMENT_1 = 'REQUIREMENT_1', ' Requirement 1'
    REQUIREMENT_2 = 'REQUIREMENT_2', ' Requirement 2'


class Permit(models.Model):
    permit_no = models.CharField(max_length=255)
    status = models.CharField(choices=Status.choices, max_length=50)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='permits')
    permittee = models.ForeignKey(
        Permittee, on_delete=models.CASCADE, blank=True, null=True, related_name='temporarily_assigned_permits')
    uploaded_file = models.FileField(
        upload_to='uploads/', null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    objects = InheritanceManager()

    def __str__(self):
        return str(self.permit_no)


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
        WildlifeCollectorPermit, on_delete=models.CASCADE, related_name='wcp_species')
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('sub_species', 'wcp')


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


class PermitApplication(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='permit_applications')
    permit_type = models.CharField(max_length=50, choices=PermitType.choices)
    status = models.CharField(choices=Status.choices, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Requirement(models.Model):
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE)
    requirement_type = models.CharField(
        max_length=50, choices=RequirementType.choices)
    uploaded_file = models.FileField(upload_to='uploads/')
