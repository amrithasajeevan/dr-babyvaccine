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





@shared_task(bind=True)
def send_mail_based_on_dates(self):
    recently_registered_user = User.objects.order_by('-date_joined').first()
    
    if recently_registered_user:
        recent_user_email = recently_registered_user.email
        children = Child.objects.filter(parent=recently_registered_user)

        for child in children:
            # Map health review dates to corresponding program IDs based on child's date of birth
            health_review_program_mapping = {
                (child.date_of_birth + timedelta(days=40)): [1],
                (child.date_of_birth + timedelta(days=67)): [2],
                (child.date_of_birth + timedelta(days=70)): [3],
                (child.date_of_birth + timedelta(days=89)): [4],
                (child.date_of_birth + timedelta(days=180)): [5],
                (child.date_of_birth + timedelta(days=304)): [6],
                (child.date_of_birth + timedelta(days=363)): [7]
            }

            for rev_date, program_ids in health_review_program_mapping.items():
                if rev_date == timezone.localtime(timezone.now()).date():
                    user = child.parent
                    mail_subject = "Health Review Date Reminder"

                    # Filter programs based on the list of program IDs
                    programs = VaccinePrograms.objects.filter(id__in=program_ids)

                    # Construct the message with vaccines and their names
                    message = f"Hi {user.username}, This is a reminder for a health review appointment today for {child.first_name}.\n"

                    if programs.exists():
                        for program in programs:
                            message += f"\nVaccines Are\n"
    
    # Use all() to get all related vaccines
                            for vaccine_info in program.vaccines.all():
                                        vaccine_name = vaccine_info.vaccine
                                        message += f"{vaccine_name}\n"
                        
                    else:
                        message += "No relevant vaccination programs found for this appointment."

                    to_email = recent_user_email
                    send_mail(
                        subject=mail_subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[to_email],
                        fail_silently=True,
                    )
                    return "done"
