

# Using Celery
Please see https://docs.celeryproject.org/en/stable/index.html for more information.
Make sure to have Redis or RabbitMQ installed and running

-  Startup Celery worker to receive tasks:

`celery -A hms_api_gateway worker -l info`

-  Startup Celery task scheduler on another shell:

`celery -A hms_api_gateway beat -l info`

-  To create an async task, do:
```
from celery import shared_task

@shared_task
def funx_name(x, y):
    return x + y
```
