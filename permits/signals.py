import logging

from django.dispatch import receiver
from django.dispatch import Signal

from .models import (
    PermitApplication
)
from .tasks import (
    notify_admins_about_submitted_application
)


logger = logging.getLogger(__name__)


application_submitted = Signal()
application_unsubmitted = Signal()


@receiver(application_submitted)
def receive_application_submitted(sender, application: PermitApplication, **kwargs):
    logger.info('Permit application %s has been submitted.', application.no)
    notify_admins_about_submitted_application.delay(
        application_id=application.id)
