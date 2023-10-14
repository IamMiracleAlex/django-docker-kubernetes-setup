from celery import shared_task


@shared_task
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    
    addition = 2+3
    return addition
