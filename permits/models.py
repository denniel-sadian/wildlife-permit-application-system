from django.db import models


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
    created_at = models.DateField()
