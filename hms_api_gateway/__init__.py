from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_api_gateway.settings')

import django

django.setup()
from .celery import app as celery_app
