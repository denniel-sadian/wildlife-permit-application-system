import logging

from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from users.models import User, TransientNotification

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
    notify_admins_about_signed_permit,
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
permit_signed = Signal()
permit_released = Signal()
permit_validated = Signal()
permit_expired = Signal()


@receiver(application_submitted)
def receive_application_submitted(sender, application: PermitApplication, **kwargs):
    message = f'Permit application {application.no} has been submitted.'
    logger.info(message)
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
            change_message=_(message)
        )


@receiver(application_unsubmitted)
def receive_application_unsubmitted(sender, application: PermitApplication, **kwargs):
    message = f'Permit application {application.no} is unsubmitted.'
    logger.info(message)
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
            change_message=_(message)
        )


@receiver(application_accepted)
def receive_application_accepted(sender, application: PermitApplication, **kwargs):
    message = f'Permit application {application.no} is accepted.'
    logger.info(message)
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
            change_message=_(message)
        )

    url = reverse_lazy('update_application', args=[application.id])
    message = f'''
    Your permit application <a href="{url}">{application.no}</a> has been accepted.
    '''
    TransientNotification.objects.create(
        user=application.client, message=message)


@receiver(application_returned)
def receive_application_returned(sender, application: PermitApplication, **kwargs):
    message = f'Permit application {application.no} is returned.'
    logger.info(message)
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
            change_message=_(message)
        )

    url = reverse_lazy('update_application', args=[application.id])
    message = f'''
    Your permit application <a href="{url}">{application.no}</a> has been returned.
    '''
    TransientNotification.objects.create(
        user=application.client, message=message)


@receiver(inspection_scheduled)
def receive_inspection_scheduled(sender, application: PermitApplication, **kwargs):
    message = f'Inspection for {application.no} has been scheduled on {application.inspection.scheduled_date}'
    logger.info(message)
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
            change_message=_(message)
        )

    url = reverse_lazy('update_application', args=[application.id])
    message = f'''
    The inspection for your permit application <a href="{url}">{application.no}</a>
    has been scheduled on {application.inspection.scheduled_date}.
    '''
    TransientNotification.objects.create(
        user=application.client, message=message)


@receiver(inspection_signed)
def receive_inspection_signed(sender, application: PermitApplication, **kwargs):
    if application is None:
        return
    message = (
        f'Inspection for {application.no} has been signed by '
        f'{application.inspection.signatures[0].name}.')
    logger.info(message)
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
            change_message=_(message)
        )


@receiver(permit_created)
def receive_permit_created(sender, permit: Permit, **kwargs):
    message = f'Permit {permit.permit_no} has been initially created.'
    logger.info(message)
    notify_signatories_about_created_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        if application:
            LogEntry.objects.log_action(
                user_id=sender.id,
                content_type_id=content_type.id,
                object_id=application.id,
                object_repr=_(str(application)),
                action_flag=CHANGE,
                change_message=_(message)
            )


@receiver(permit_signed)
def receive_permit_signed(sender, permit: Permit, **kwargs):
    message = f'Permit {permit.permit_no} has been signed by {permit.signatures.first().person.name}.'
    logger.info(message)
    notify_admins_about_signed_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        if application:
            LogEntry.objects.log_action(
                user_id=sender.id,
                content_type_id=content_type.id,
                object_id=application.id,
                object_repr=_(str(application)),
                action_flag=CHANGE,
                change_message=_(message)
            )


@receiver(permit_released)
def receive_permit_released(sender, permit: Permit, **kwargs):
    message = f'Permit {permit.permit_no} has been released.'
    logger.info(message)
    notify_client_and_admins_about_released_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        if application:
            LogEntry.objects.log_action(
                user_id=sender.id,
                content_type_id=content_type.id,
                object_id=application.id,
                object_repr=_(str(application)),
                action_flag=CHANGE,
                change_message=_(message)
            )

    url = reverse_lazy('permit_detail', args=[permit.id])
    message = f'''
    Your permit <a href="{url}">{permit.permit_no}</a> has been released!
    '''
    TransientNotification.objects.create(
        user=permit.client, message=message)


@receiver(permit_validated)
def receive_permit_validated(sender, permit: Permit, **kwargs):
    message = f'Permit {permit.permit_no} has been validated.'
    logger.info(message)
    notify_client_and_admins_about_validated_permit.delay(
        permit_id=permit.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        application = PermitApplication.objects.filter(permit=permit).first()
        if application:
            LogEntry.objects.log_action(
                user_id=sender.id,
                content_type_id=content_type.id,
                object_id=application.id,
                object_repr=_(str(application)),
                action_flag=CHANGE,
                change_message=_(message)
            )

    url = reverse_lazy('permit_detail', args=[permit.id])
    message = f'''
    Your permit <a href="{url}">{permit.permit_no}</a> has been validated successfully.
    '''
    TransientNotification.objects.create(
        user=permit.client, message=message)
