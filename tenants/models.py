from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Hospital(TenantMixin):
    name = models.CharField(max_length=150)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    def __str__(self):
        return self.domain
