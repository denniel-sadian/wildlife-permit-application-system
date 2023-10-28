import logging

from django.dispatch import receiver
from django.dispatch import Signal

from .models import (
    PermitApplication
)
from .tasks import (
    notify_admins_about_submitted_application,
    notify_admins_about_unsubmitted_application,
    notify_client_about_accepted_application,
    notify_client_about_returned_application
)


logger = logging.getLogger(__name__)


application_submitted = Signal()
application_unsubmitted = Signal()
application_accepted = Signal()
application_returned = Signal()


@receiver(application_submitted)
def receive_application_submitted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s has been submitted.', application.no)
    notify_admins_about_submitted_application.delay(
        application_id=application.id)


@receiver(application_unsubmitted)
def receive_application_unsubmitted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s is unsubmitted.', application.no)
    notify_admins_about_unsubmitted_application.delay(
        application_id=application.id)


@receiver(application_accepted)
def receive_application_accepted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s is accepted.', application.no)
    notify_client_about_accepted_application.delay(
        application_id=application.id)


@receiver(application_returned)
def receive_application_returned(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s is returned.', application.no)
    notify_client_about_returned_application.delay(
        application_id=application.id)
