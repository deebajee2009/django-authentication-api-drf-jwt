"""
Accounts app tasks
"""
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import User


@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)

    subject = "به سایت ما خوش آمدید"

    text_content = render_to_string(
        "emails/welcome_fa.txt",
        {"user": user},
    )

    html_content = render_to_string(
        "emails/welcome_fa.html",
        {"user": user},
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


@shared_task
def send_reset_password_email(user_id, link):
    user = User.objects.get(id=user_id)

    subject = "بازیابی رمز عبور"

    text_content = render_to_string(
        "emails/password_recovery_fa.txt",
        {"link": link},
    )

    html_content = render_to_string(
        "emails/password_recovery_fa.html",
        {"linl": link},
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
