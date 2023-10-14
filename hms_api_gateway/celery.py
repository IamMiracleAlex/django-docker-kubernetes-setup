import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_api_gateway.settings')
app = Celery('hms_api_gateway')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.conf.update(timezone='Africa/Lagos', enable_utc=True, )
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {

	"sample_tasks": {
		"task": "accounts.tasks.get_users_count",
		'schedule': crontab(minute="*/1"),  # every minute
	},
}
