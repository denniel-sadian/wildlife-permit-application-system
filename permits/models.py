from django.db import models
from django.utils import timezone

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
    WCP = 'WCP', "Wildlife Collector's Permit"
    LTP = 'LTP', 'Local Transport Permit'
    CWR = 'CWR', 'Certificate of Wildlife Registration'
    GP = 'GP', 'Gratuitous Permit'


class RequirementType(models.TextChoices):
    PRIOR_CLEARANCE_FROM_AFFECTED_COMMUNITIES = (
        'PRIOR_CLEARANCE_FROM_AFFECTED_COMMUNITIES',
        'Prior clearance from the affected communities, i.e. concerned LGUs, recognized head people in accordance with R.A. 8371, or PAMB')
    # WFP
    CERT_OF_REGISTRATION = (
        'CERT_OF_REGISTRATION',
        'Copy of Certificate of Registration from appropriate Government agencies')
    SCIENTIFIC_EXPERTISE_PROOF = (
        'SCIENTIFIC_EXPERTISE_PROOF',
        'Proof of scientific expertise (list of qualifications of manpower)')
    FINANCIAL_PLAN = (
        'FINANCIAL_PLAN',
        'Financial plan showing financial capability to go into breeding')
    PROPOSED_FACILITY_DESIGN = (
        'PROPOSED_FACILITY_DESIGN', 'Proposed facility design')
    LETTER_OF_COMMITMENT = (
        'LETTER_OF_COMMITMENT',
        'In case of indigenous threatened species, letter of commitment to simultaneously undertake conservation breeding and propose measures on rehabilitation and/or protection of habitat, where appropriate, as may be determined by the RWMC')
    # WCP
    CITIZENSHIP = (
        'CITIZENSHIP',
        'Citizenship verification papers, if citizenship is by Naturalization')
    # LTP
    DOCUMENTS_SUPPORTING_LEGAL_POSSESSION_OF_WILDLIFE = (
        'DOCUMENTS_SUPPORTING_LEGAL_POSSESSION_OF_WILDLIFE',
        'Documents supporting the legal possession/ acquisition of wildlife')
    PHYTOSANITARY_OR_VETERINARY_CERT = (
        'PHYTOSANITARY_OR_VETERINARY_CERT',
        'Phytosanitary Certificate (for plants) or Veterinary Quarantine Certificate (for animals) from the concerned Department of Agriculture (DA) Office.')


class RequirementList(models.Model):
    permit_type = models.CharField(
        max_length=50, choices=PermitType.choices, unique=True)

    def __str__(self):
        return 'Requirements for ' + self.get_permit_type_display()


class RequirementItem(models.Model):
    requirement_list = models.ForeignKey(
        RequirementList, on_delete=models.CASCADE, related_name='items')
    requirement = models.CharField(
        max_length=1000, choices=RequirementType.choices)
    optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ('requirement_list', 'requirement')


class Permit(models.Model):
    permit_no = models.CharField(max_length=255)
    status = models.CharField(choices=Status.choices, max_length=50)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE, blank=True, null=True, related_name='permits')
    permittee = models.ForeignKey(
        'users.Permittee', on_delete=models.CASCADE, blank=True, null=True, related_name='temporarily_assigned_permits')
    uploaded_file = models.FileField(
        upload_to='uploads/', null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    objects = InheritanceManager()

    @property
    def current_status(self):
        if self.valid_until:
            is_still_valid = self.valid_until >= timezone.now().date()
            if not is_still_valid:
                return Status.EXPIRED
        return self.status

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
        WildlifeCollectorPermit, on_delete=models.CASCADE, related_name='allowed_species')
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('sub_species', 'wcp')

    def __str__(self):
        return str(self.sub_species)


class LocalTransportPermit(Permit):
    wfp = models.ForeignKey(
        WildlifeFarmPermit, on_delete=models.CASCADE, related_name='wfp_ltps')
    wcp = models.ForeignKey(
        WildlifeFarmPermit, on_delete=models.CASCADE, related_name='wcp_ltps')
    transport_location = models.CharField(max_length=255)
    transport_date = models.DateField()

    class Meta:
        verbose_name = "Local Transport Permit"


class PermitApplication(models.Model):
    no = models.CharField(max_length=255)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE, related_name='permit_applications')
    permit_type = models.CharField(max_length=50, choices=PermitType.choices)
    status = models.CharField(choices=Status.choices, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # LTP
    transport_date = models.DateField(null=True, blank=True)

    # WCP
    names_and_addresses_of_authorized_collectors_or_trappers = models.TextField(
        null=True, blank=True)

    def __str__(self):
        return str(self.no)


class TransportEntry(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='transportings')
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name='requested_species_to_transport',
        blank=True, null=True)
    ltp = models.ForeignKey(
        LocalTransportPermit, on_delete=models.CASCADE, related_name='species_to_transport',
        blank=True, null=True)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('sub_species', 'permit_application')


class CollectionEntry(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='collections')
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name='requested_species',
        blank=True, null=True)
    wcp = models.ForeignKey(
        WildlifeCollectorPermit, on_delete=models.CASCADE, related_name='allowed_animals',
        blank=True, null=True)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('sub_species', 'permit_application')

    def __str__(self):
        return str(self.sub_species)


class Requirement(models.Model):
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name='requirements')
    requirement_type = models.CharField(
        max_length=50, choices=RequirementType.choices, null=False, blank=False)
    uploaded_file = models.FileField(
        upload_to='uploads/', null=False, blank=False)

    class Meta:
        unique_together = ('permit_application', 'requirement_type')
