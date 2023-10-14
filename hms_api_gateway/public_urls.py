"""hms_api_gateway URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from hms_api_gateway import urls


def schema_view(version: int):
	return get_schema_view(
		patterns=urls.swagger_url[version],
		info=openapi.Info(
			title=f"Heckerbella HMS API",
			default_version=f'Version {version}',
			terms_of_service="https://www.heckerbella.com/",
			license=openapi.License(name="BSD License"),
		),
		public=True,
		permission_classes=(permissions.AllowAny,),
	)


urlpatterns = [
		path('swagger/v1', schema_view(1).with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
		path('swagger/v2', schema_view(2).with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
		path('', include('hms_api_gateway.urls')),
	] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
																					document_root=settings.MEDIA_ROOT)
