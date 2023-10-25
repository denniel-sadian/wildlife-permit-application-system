import logging

from celery import shared_task

from .emails import RegistrationEmailView
from .models import User


logger = logging.getLogger(__name__)


@shared_task
def send_account_created_email(user_id, temporary_password):
    user = User.objects.get(id=user_id)
    logger.info('Sending account created email to %s...', user.email)
    RegistrationEmailView(user, temporary_password).send()
    logger.info('Account created email sent to %s.', user.email)
