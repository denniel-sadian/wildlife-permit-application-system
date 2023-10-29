import copy
import logging
from datetime import datetime


from django.contrib.auth.models import Group

from celery import shared_task

from users.models import (
    User,
    Admin
)

from .models import (
    PermitApplication,
    Status,
    Permit,
    LocalTransportPermit
)
from .emails import (
    SubmittedApplicationEmailView,
    UnsubmittedApplicationEmailView,
    AcceptedApplicationEmailView,
    ReturnedApplicationEmailView,
    ScheduledInspectionEmailView,
    AssignedScheduledInspectionEmailView,
    SignedInspectionEmailView,
    PermitCreatedEmailView,
    PermitReleasedEmailView,
    PermitValidatedEmailView,
    PermitExpiredEmailView
)


logger = logging.getLogger(__name__)


def get_admins_who_can_receive_emails():
    admins = Admin.objects.filter(
        is_active=True, is_initial_password_changed=True)
    return admins


def get_permit_signatories_who_can_receive_emails():
    group = Group.objects.get(name='Permit Signatory')
    signatories = User.objects.filter(
        groups=group, is_active=True, is_initial_password_changed=True)
    return signatories


@shared_task
def notify_admins_about_submitted_application(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    admins = get_admins_who_can_receive_emails()
    for admin in admins:
        SubmittedApplicationEmailView(admin, application).send()


@shared_task
def notify_admins_about_unsubmitted_application(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    admins = get_admins_who_can_receive_emails()
    for admin in admins:
        UnsubmittedApplicationEmailView(admin, application).send()


@shared_task
def notify_client_about_accepted_application(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    AcceptedApplicationEmailView(application.client, application).send()


@shared_task
def notify_client_about_returned_application(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    ReturnedApplicationEmailView(application.client, application).send()


@shared_task
def notify_client_and_officer_about_scheduled_inspection(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    ScheduledInspectionEmailView(
        application.client, application).send()
    AssignedScheduledInspectionEmailView(
        application.inspection.inspecting_officer, application).send()


@shared_task
def notify_admins_about_signed_inspection(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    admins = get_admins_who_can_receive_emails()
    for admin in admins:
        if admin.id != application.inspection.signatures.first().person.id:
            SignedInspectionEmailView(
                admin, application).send()


@shared_task
def notify_signatories_about_created_permit(permit_id):
    permit: Permit = Permit.objects.get(id=permit_id).subclass

    notifiable_permits = [LocalTransportPermit.__name__]
    if permit.type not in notifiable_permits:
        return

    signatories = get_permit_signatories_who_can_receive_emails()
    for signatory in signatories:
        PermitCreatedEmailView(signatory, permit).send()


@shared_task
def notify_client_and_admins_about_released_permit(permit_id):
    permit: Permit = Permit.objects.get(id=permit_id).subclass
    users = list(get_admins_who_can_receive_emails())
    users.append(permit.client)
    for user in users:
        PermitReleasedEmailView(user, permit).send()


@shared_task
def notify_client_and_admins_about_validated_permit(permit_id):
    permit: Permit = Permit.objects.get(id=permit_id).subclass
    users = list(get_admins_who_can_receive_emails())
    users.append(permit.client)
    for user in users:
        PermitValidatedEmailView(user, permit).send()


@shared_task
def check_permit_validity():
    logger.info('Checking for permits to expire...')

    permits_to_expire = Permit.objects.filter(
        status__in=[Status.RELEASED],
        valid_until__lt=datetime.now().date())
    admins = list(get_admins_who_can_receive_emails())

    for permit in permits_to_expire:
        permit.status = Status.EXPIRED
        permit.save()
        logger.info('Permit %s has expired already.', permit.permit_no)

        # Notify the users
        users = copy.deepcopy(admins)
        users.append(permit.client)
        for user in users:
            PermitExpiredEmailView(user, permit.subclass).send()

    logger.info('Done expiring permits.')
