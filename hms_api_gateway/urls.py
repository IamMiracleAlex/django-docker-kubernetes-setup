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
from django.urls import path, include
from django.contrib import admin

swagger_pattern1 = [
                path('v1/', include("hms_api_gateway.versions.v1")),
              ]
swagger_pattern2 = [
                path('v2/', include('hms_api_gateway.versions.v2'))
              ]
swagger_url = {1: swagger_pattern1, 2: swagger_pattern2}

urlpatterns = [
                path('admin/', admin.site.urls),
                path('v1/', include("hms_api_gateway.versions.v1",)),
                path('v2/', include('hms_api_gateway.versions.v2', ))
              ]