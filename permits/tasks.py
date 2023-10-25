import logging
from datetime import datetime

from celery import shared_task

from .models import (
    Status,
    Permit
)


logger = logging.getLogger(__name__)


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
