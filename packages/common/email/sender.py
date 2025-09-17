from django.core.mail import EmailMessage
from django.conf import settings


def send_email(to: list[str], subject: str, body: str, attachments: list = None) -> None:
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
    )
    if attachments:
        for filename, content, mimetype in attachments:
            email.attach(filename, content, mimetype)
    email.send(fail_silently=False)
