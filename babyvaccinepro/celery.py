from __future__ import absolute_import,unicode_literals
import os 
from celery.schedules import crontab

from celery import Celery
from django.conf import settings
# from django_celery_beat.models import PeriodicTask

os.environ.setdefault('DJANGO_SETTINGS_MODULE','babyvaccinepro.settings')


app=Celery('babyvaccinepro')
app.conf.enable_utc=False

app.conf.beat_schedule = {
    #  'send-health-review-reminders': {
    #     'task': 'babyapp.tasks.send_mail_based_on_dates',
    #     'schedule': crontab(hour=15, minute=50),
    # },

}

app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings,namespace='CELERY')

app.autodiscover_tasks()
@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request!r}')