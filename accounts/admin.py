
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
