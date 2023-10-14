from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name',)
