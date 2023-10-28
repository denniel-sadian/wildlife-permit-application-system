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
    SubmittedApplicationEmailView
)


logger = logging.getLogger(__name__)


@shared_task
def notify_admins_about_submitted_application(application_id):
    application: PermitApplication = PermitApplication.objects.get(
        id=application_id)
    admins = Admin.objects.filter(
        is_active=True, is_initial_password_changed=True)
    for admin in admins:
        SubmittedApplicationEmailView(admin, application).send()


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
