from django.conf import settings
from rest_framework.routers import DefaultRouter,  SimpleRouter

from accounts.views import UserAPI

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register('user', UserAPI, basename='user')


urlpatterns = router.urls
