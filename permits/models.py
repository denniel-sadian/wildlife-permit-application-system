from datetime import timedelta
import json
import base64

from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.conf import settings
from django.core.validators import MinValueValidator

from model_utils.managers import InheritanceManager

from users.mixins import ModelMixin
from users.mixins import (
    validate_file_extension,
    validate_amount,
    validate_file_size
)
from animals.models import SubSpecies


class Status(models.TextChoices):
    DRAFT = 'DRAFT', 'On Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    RETURNED = 'RETURNED', 'Returned'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    RELEASED = 'RELEASED', 'Released'
    USED = 'USED', 'Used'
    EXPIRED = 'EXPIRED', 'Expired'


class PermitType(models.TextChoices):
    WFP = 'WFP', 'Wildlife Farm Permit'
    WCP = 'WCP', "Wildlife Collector's Permit"
    LTP = 'LTP', 'Local Transport Permit'
    CWR = 'CWR', 'Certificate of Wildlife Registration'
    GP = 'GP', 'Gratuitous Permit'


class Requirement(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)
    example_file = models.FileField(
        upload_to='example-requirements/', null=True, blank=True,
        validators=[validate_file_size])

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
    permit_no = models.CharField(max_length=255, unique=True)
    status = models.CharField(choices=Status.choices, max_length=50)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE, null=True, related_name='permits')
    uploaded_file = models.FileField(
        upload_to='uploads/', null=True,
        validators=[validate_file_extension, validate_file_size])
    valid_until = models.DateField(null=True, blank=True)
    or_no = models.CharField('Order No.', max_length=100, null=True)
    or_no_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_amount],
        null=True)
    created_at = models.DateField(auto_now_add=True)
    issued_date = models.DateField(null=True)
    payment_order = models.ForeignKey(
        'payments.PaymentOrder', on_delete=models.SET_NULL, null=True)
    inspection = models.ForeignKey(
        'Inspection', on_delete=models.SET_NULL, null=True)
    farm_name = models.CharField(max_length=255, null=True)
    farm_address = models.CharField(max_length=255, null=True)

    objects = InheritanceManager()

    @property
    def current_status(self):
        if self.valid_until:
            is_still_valid = self.valid_until >= timezone.now().date()
            if not is_still_valid:
                self.status = Status.EXPIRED
                self.save()
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

    @property
    def validation_url(self):
        data = json.dumps(
            {'permit_no': self.permit_no or '', 'or_no': self.or_no or ''})
        url_safe_base64 = base64.urlsafe_b64encode(
            data.encode('utf-8')).decode('utf-8')
        path = reverse_lazy('validate_permit')
        return f'{path}?data={url_safe_base64}'

    def calculate_validity_date(self):
        if self.issued_date:
            days_valid = settings.VALIDITY[self.type]
            valid_until = self.issued_date + timedelta(days=days_valid)
            self.valid_until = valid_until

    def save(self, *args, **kwargs):
        if self.status == Status.RELEASED:
            if application := self.application:
                application.status = self.status
                application.save()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.permit_no)


class WildlifeFarmPermit(Permit):

    class Meta:
        verbose_name = "Wildlife Farm Permit"

    @property
    def permit_type(self):
        return PermitType.WFP.label


class WildlifeCollectorPermit(Permit):

    class Meta:
        verbose_name = "Wildlife Collector's Permit"

    @property
    def permit_type(self):
        return PermitType.WCP.label


class GratuitousPermit(Permit):

    @property
    def permit_type(self):
        return PermitType.GP.label


class CertificateOfWildlifeRegistration(Permit):

    @property
    def permit_type(self):
        return PermitType.CWR.label


class PermittedToCollectAnimal(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='species_permitted')
    wcp = models.ForeignKey(
        WildlifeCollectorPermit, on_delete=models.CASCADE, related_name='allowed_species')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('sub_species', 'wcp')

    def __str__(self):
        return str(self.sub_species)


class LocalTransportPermit(Permit):
    wfp = models.ForeignKey(
        WildlifeFarmPermit, verbose_name='Wildlife Farm Permit',
        on_delete=models.CASCADE, related_name='wfp_ltps')
    wcp = models.ForeignKey(
        WildlifeCollectorPermit, verbose_name="Wildlife Collector's Permit",
        on_delete=models.CASCADE, related_name='wcp_ltps')
    transport_location = models.CharField(max_length=255)
    transport_date = models.DateField()

    class Meta:
        verbose_name = 'Local Transport Permit'

    @property
    def permit_type(self):
        return PermitType.LTP.label

    @property
    def total_transport_quantity(self):
        return self.species_to_transport.aggregate(
            total=Coalesce(Sum(F('quantity')), Value(0, models.IntegerField())))['total']

    @property
    def amount(self):
        if self.payment_order:
            return self.payment_order.payment.amount
        else:
            return self.or_no_amount

    @property
    def receipt_no(self):
        if self.payment_order:
            return self.payment_order.payment.receipt_no
        else:
            return self.or_no


class PermitApplication(ModelMixin, models.Model):
    no = models.CharField(max_length=255)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE, related_name='permit_applications')
    permit_type = models.CharField(max_length=50, choices=PermitType.choices)
    status = models.CharField(choices=Status.choices, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    farm_name = models.CharField(max_length=255, null=True, blank=True)
    farm_address = models.CharField(max_length=255, null=True, blank=True)

    # LTP
    transport_date = models.DateField(null=True, blank=True)
    transport_location = models.CharField(
        max_length=255, null=True, blank=True)

    # WCP
    names_and_addresses_of_authorized_collectors_or_trappers = models.TextField(
        null=True, blank=True)

    # The permit created
    permit = models.ForeignKey(
        Permit, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def total_transport_quantity(self):
        return self.requested_species_to_transport.aggregate(
            total=Coalesce(Sum(F('quantity')), Value(0, models.IntegerField())))['total']

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
            if not self.transport_date:
                return False
            if not self.transport_location:
                return False

        # For WCP
        if self.permit_type == PermitType.WCP:
            needed_fields = [
                'names_and_addresses_of_authorized_collectors_or_trappers',
                'farm_name', 'farm_address']
            for field in needed_fields:
                if not hasattr(self, field) or (hasattr(self, field) and not getattr(self, field)):
                    return False
            if self.requested_species.count() == 0:
                return False

        # For WFP
        if self.permit_type == PermitType.WFP:
            needed_fields = ['farm_name', 'farm_address']
            for field in needed_fields:
                if not hasattr(self, field) or (hasattr(self, field) and not getattr(self, field)):
                    return False

        return True

    def __str__(self):
        return str(self.no)


class TransportEntry(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='transportings',
        verbose_name='Species')
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name='requested_species_to_transport',
        blank=True, null=True)
    ltp = models.ForeignKey(
        LocalTransportPermit, on_delete=models.SET_NULL, related_name='species_to_transport',
        blank=True, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.CharField(max_length=100)

    class Meta:
        unique_together = ('sub_species', 'permit_application')


class CollectionEntry(models.Model):
    sub_species = models.ForeignKey(
        SubSpecies, on_delete=models.CASCADE, related_name='collections',
        verbose_name='Species')
    permit_application = models.ForeignKey(
        PermitApplication, on_delete=models.CASCADE, related_name='requested_species',
        blank=True, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

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
        upload_to='requirements/', null=False, blank=False,
        validators=[validate_file_size])

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
    no = models.CharField(max_length=255, unique=True)
    permit_application = models.OneToOneField(
        PermitApplication, on_delete=models.CASCADE,
        null=True)
    scheduled_date = models.DateField(null=True)
    inspecting_officer = models.ForeignKey(
        'users.Admin', on_delete=models.CASCADE, null=True)

    @property
    def day(self):
        if self.scheduled_date:
            if 10 <= self.scheduled_date.day % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(
                    self.scheduled_date.day % 10, 'th')
            return f'{self.scheduled_date.day}{suffix}'

    @property
    def month_and_year(self):
        if self.scheduled_date:
            month = self.scheduled_date.strftime('%B')
            return f'{month} {self.scheduled_date.year}'

    @property
    def client(self):
        if self.permit_application is not None:
            return self.permit_application.client
        else:
            permit = Permit.objects.filter(inspection=self).first()
            if permit:
                return permit.client

    @property
    def transports(self):
        if self.permit_application is not None:
            return self.permit_application.requested_species_to_transport
        else:
            permit = Permit.objects.filter(inspection=self).first()
            if permit:
                return permit.subclass.species_to_transport

    @property
    def total_transport_quantity(self):
        if self.permit_application is not None:
            return self.permit_application.requested_species_to_transport.aggregate(
                total=Coalesce(Sum(F('quantity')), Value(0, models.IntegerField())))['total']
        else:
            permit = Permit.objects.filter(inspection=self).first()
            if permit:
                return permit.subclass.species_to_transport.aggregate(
                    total=Coalesce(Sum(F('quantity')), Value(0, models.IntegerField())))['total']

    def __str__(self):
        return str(self.no)


class Signature(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    person = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    @staticmethod
    def create(user, obj):
        sign = obj.signatures.filter(person=user).first()
        if sign:
            return sign
        elif user.title and user.signature_image:
            sign = Signature(person=user, content_object=obj)
            sign.save()
            return sign

    @staticmethod
    def remove(user, obj):
        for sign in obj.signatures:
            if sign.person == user:
                sign.delete()


class Validation(models.Model):
    validated_at = models.DateTimeField(auto_now_add=True)
    validator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    permit = models.OneToOneField(Permit, on_delete=models.CASCADE)
