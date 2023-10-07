from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy

from model_utils.managers import InheritanceManager

from users.mixins import ModelMixin
from animals.models import SubSpecies


class Status(models.TextChoices):
    DRAFT = 'DRAFT', 'On Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    RETURNED = 'RETURNED', 'Returned'
    ACCEPTED = 'ACCEPTED', 'Accepted'
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
        'Documents supporting the legal possession/acquisition of wildlife')
    PHYTOSANITARY_OR_VETERINARY_CERT = (
        'PHYTOSANITARY_OR_VETERINARY_CERT',
        'Phytosanitary Certificate (for plants) or Veterinary Quarantine Certificate (for animals) from the concerned Department of Agriculture (DA) Office.')

    # CWP
    ACQUISITION_PROOF_OR_DEEDS_OF_DONATION = 'ACQUISITION_PROOF_OR_DEEDS_OF_DONATION', 'Proof of Acquisition/Deeds of Donation'

    # GW
    ENDORSEMENT_LETTER = 'ENDORSEMENT_LETTER', 'Endorsement letter from dead/recognized expert/conservation organization'
    COPY_OF_RESEARCH_THESIS_DISSERTATION = 'COPY_OF_RESEARCH_THESIS_DISSERTATION', 'Copy of the research/thesis/dissertation proposals, or copy of the affidavit of undertaking/approved memorandum of agreement (MOA)'


class Requirement(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return str(self.label)

    def save(self, *args, **kwargs):
        self.code = self.code.upper().replace(' ', '')
        super().save(*args, **kwargs)


class RequirementList(models.Model):
    permit_type = models.CharField(
        max_length=50, choices=PermitType.choices, unique=True)

    def __str__(self):
        return 'Requirements for ' + self.get_permit_type_display()


class RequirementItem(models.Model):
    requirement_list = models.ForeignKey(
        RequirementList, on_delete=models.CASCADE, related_name='items')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ('requirement_list', 'requirement')


class Permit(ModelMixin, models.Model):
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

    @property
    def admin_url(self):
        permit = self.subclass
        path = f'admin:{permit._meta.app_label}_{permit._meta.model_name}_change'
        return reverse_lazy(path, args=[permit.id])

    @property
    def preview_url(self):
        return reverse_lazy('permit_detail', args=[self.id])

    @property
    def application(self):
        application = PermitApplication.objects.filter(permit=self).first()
        return application

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
        WildlifeCollectorPermit, on_delete=models.CASCADE, related_name='wcp_ltps')
    transport_location = models.CharField(max_length=255)
    transport_date = models.DateField()

    class Meta:
        verbose_name = "Local Transport Permit"


class PermitApplication(ModelMixin, models.Model):
    no = models.CharField(max_length=255)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE, related_name='permit_applications')
    permit_type = models.CharField(max_length=50, choices=PermitType.choices)
    status = models.CharField(choices=Status.choices, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # LTP
    transport_date = models.DateField(null=True, blank=True)
    transport_location = models.CharField(
        max_length=255, null=True, blank=True)

    # WCP
    names_and_addresses_of_authorized_collectors_or_trappers = models.TextField(
        null=True, blank=True)

    # The permit created
    permit = models.ForeignKey(
        Permit, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def needed_requirements(self):
        needed_requirements = []
        for needed_requirement in RequirementList.objects.get(permit_type=self.permit_type).items.all():
            uploaded_requirement = UploadedRequirement.objects.filter(requirement=needed_requirement.requirement,
                                                                      permit_application=self).first()
            needed_requirements.append({
                'requirement': needed_requirement,
                'submitted': uploaded_requirement is not None,
                'optional': needed_requirement.optional,
            })
        return needed_requirements

    @property
    def needed_requirements_are_submitted(self):
        for requirement in self.needed_requirements:
            if not requirement['optional'] and not requirement['submitted']:
                return False
        return True

    @property
    def editable(self):
        return self.status in (Status.DRAFT, Status.RETURNED)

    @property
    def submittable(self):
        # Make sure the requirements are submitted
        if not self.needed_requirements_are_submitted:
            return False

        # For LTP
        if self.permit_type == PermitType.LTP:
            if self.requested_species_to_transport.count() == 0:
                return False
            if self.transport_date is None:
                return False

        # For WCP
        if self.permit_type == PermitType.WCP:
            if self.requested_species.count() == 0:
                return False
            if self.names_and_addresses_of_authorized_collectors_or_trappers is None:
                return False

        return True

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


class UploadedRequirement(models.Model):
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name='requirements')
    requirement = models.ForeignKey(
        Requirement, on_delete=models.CASCADE)
    uploaded_file = models.FileField(
        upload_to='requirements/', null=False, blank=False)

    class Meta:
        unique_together = ('permit_application', 'requirement')


class Remarks(models.Model):
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name="remarks")
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Inspection(ModelMixin, models.Model):
    permit_application = models.OneToOneField(
        PermitApplication, on_delete=models.CASCADE)
    scheduled_date = models.DateField(blank=True, null=True)
    inspecting_officer = models.ForeignKey(
        'users.Admin', on_delete=models.CASCADE, blank=True, null=True)
    report_file = models.FileField(
        upload_to='inspection_reports/', blank=True, null=True)

    def __str__(self):
        return f'Inspection on {self.scheduled_date} for application {self.permit_application}'
