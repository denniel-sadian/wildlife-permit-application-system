import logging

from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from users.models import User

from .models import (
    PermitApplication,
    Permit
)
from .tasks import (
    notify_admins_about_submitted_application,
    notify_admins_about_unsubmitted_application,
    notify_client_about_accepted_application,
    notify_client_about_returned_application,
    notify_client_and_officer_about_scheduled_inspection,
    notify_admins_about_signed_inspection,
    notify_signatories_about_created_permit,
    notify_client_and_admins_about_released_permit,
    notify_client_and_admins_about_validated_permit
)


logger = logging.getLogger(__name__)


application_submitted = Signal()
application_unsubmitted = Signal()
application_accepted = Signal()
application_returned = Signal()
inspection_scheduled = Signal()
inspection_signed = Signal()
permit_created = Signal()
permit_released = Signal()
permit_validated = Signal()
permit_expired = Signal()


@receiver(application_submitted)
def receive_application_submitted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s has been submitted.', application.no)
    notify_admins_about_submitted_application.delay(
        application_id=application.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit application was submitted.')
        )


@receiver(application_unsubmitted)
def receive_application_unsubmitted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s is unsubmitted.', application.no)
    notify_admins_about_unsubmitted_application.delay(
        application_id=application.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit application was unsubmitted.')
        )


@receiver(application_accepted)
def receive_application_accepted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s is accepted.', application.no)
    notify_client_about_accepted_application.delay(
        application_id=application.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit application was accepted.')
        )


@receiver(application_returned)
def receive_application_returned(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s is returned.', application.no)
    notify_client_about_returned_application.delay(
        application_id=application.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit application was returned.')
        )


@receiver(inspection_scheduled)
def receive_inspection_scheduled(sender, application: PermitApplication, **kwargs):
    logger.info('Inspection for %s has been scheduled.', application.no)
    notify_client_and_officer_about_scheduled_inspection.delay(
        application_id=application.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_(
                f'Inspection was scheduled to be on {application.inspection.scheduled_date}')
        )


@receiver(inspection_signed)
def receive_inspection_signed(sender, application: PermitApplication, **kwargs):
    logger.info('Inspection for %s has been signed.', application.no)
    notify_admins_about_signed_inspection.delay(
        application_id=application.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_(
                f'Inspection was signed by {application.inspection.inspecting_officer.name}')
        )


@receiver(permit_created)
def receive_permit_created(sender, permit: Permit, **kwargs):
    logger.info('Permit %s has been created.', permit.permit_no)
    notify_signatories_about_created_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit was initially created.')
        )


@receiver(permit_released)
def receive_permit_released(sender, permit: Permit, **kwargs):
    logger.info('Permit %s has been released.', permit.permit_no)
    notify_client_and_admins_about_released_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit was released.')
        )


@receiver(permit_validated)
def receive_permit_validated(sender, permit: Permit, **kwargs):
    logger.info('Permit %s has been validated.', permit.permit_no)
    notify_client_and_admins_about_validated_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=application.id,
            object_repr=_(str(application)),
            action_flag=CHANGE,
            change_message=_('Permit was released.')
        )
