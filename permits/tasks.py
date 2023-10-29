import logging
from datetime import datetime

from celery import shared_task

from users.models import (
    Admin
)

from .models import (
    PermitApplication,
    Status,
    Permit
)
from .emails import (
    SubmittedApplicationEmailView,
    UnsubmittedApplicationEmailView,
    AcceptedApplicationEmailView,
    ReturnedApplicationEmailView,
    ScheduledInspectionEmailView,
    AssignedScheduledInspectionEmailView,
    SignedInspectionEmailView
)


logger = logging.getLogger(__name__)


def get_admins_who_can_receive_emails():
    admins = Admin.objects.filter(
        is_active=True, is_initial_password_changed=True)
    return admins


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
def check_permit_validity():
    logger.info('Checking for permits to expire...')

    permits_to_expire = Permit.objects.filter(
        status__in=[Status.RELEASED],
        valid_until__lt=datetime.now().date())
    for permit in permits_to_expire:
        permit.status = Status.EXPIRED
        permit.save()
        logger.info('Permit %s has expired already.', permit.permit_no)

    logger.info('Done expiring permits.')
