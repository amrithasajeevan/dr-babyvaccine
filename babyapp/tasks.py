from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from datetime import timedelta
from django.core.mail import send_mail
from babyvaccinepro import settings
from .models import *

from datetime import datetime, timedelta
from django.utils import timezone

# @shared_task(bind=True)
# def send_mail_func(self):
#     users = User.objects.all()
#     #timezone.localtime(users.date_time)+timedelta(days=2)
#     for user in users:
#         mail_subject = "hi celery testing"
#         message = "checking celery, just a trial"
#         to_email = user.email 
#         send_mail(
#             subject=mail_subject,
#             message=message,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[to_email],
#             fail_silently=True
#         )
#     return "done"

# from datetime import datetime, timedelta  

@shared_task(bind=True)
def send_mail_based_on_dates(self):
    recently_registered_user = User.objects.order_by('-date_joined').first()
    if recently_registered_user:
        recent_user_email = recently_registered_user.email
    children = Child.objects.filter(parent=recently_registered_user)
    
    for child in children:
        health_rev_dates = (
            # timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=1), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=40), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=67), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=70), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=89), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=180), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=304), datetime.min.time())),
            timezone.make_aware(datetime.combine(child.date_of_birth + timedelta(days=363), datetime.min.time())),
            
            
        )

        for rev_date in health_rev_dates:
            if timezone.localtime(rev_date).date() == timezone.localtime(timezone.now()).date():
                user = child.parent  # Assuming Child has a ForeignKey to Parent
                mail_subject = "Health Review Date Reminder"
                message = f"Hi {user.username}, This is a reminder for a health review appointment today for {child.first_name}."
                to_email = recent_user_email
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[to_email],
                    fail_silently=True,
                )

    return "Done"