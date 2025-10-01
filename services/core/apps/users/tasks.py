import os
from celery import shared_task
from django.core.mail import send_mail


DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')


@shared_task
def send_password_reset_email(subject: str, recipient: str, body: str):
    send_mail(
        subject,
        body,
        DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=False,
    )
