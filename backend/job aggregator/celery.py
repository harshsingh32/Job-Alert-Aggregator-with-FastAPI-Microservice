import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobaggregator.settings')

app = Celery('jobaggregator')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'scrape-jobs-every-hour': {
        'task': 'jobs.tasks.scrape_all_jobs',
        'schedule': 3600.0,  # Run every hour
    },
    'send-job-alerts': {
        'task': 'jobs.tasks.send_job_alerts',
        'schedule': 7200.0,  # Run every 2 hours
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')