from django.db import connection
from django_tenants.middleware import TenantMainMiddleware
from decouple import config
from .classes import SchemaFromRequest, SchemaToTenant


class TenantMiddleware(TenantMainMiddleware):
    def __init__(self, get_response=None):
        super().__init__(get_response=get_response)

    def process_request(self, request):
        try:
            hostname = self.hostname_from_request(request)
            if hostname == 'localhost':
                schema = SchemaFromRequest(request)
            else:
                schema = hostname.split(f".{config('DOMAIN')}")[0]
            if schema == 'public':
                connection.set_schema_to_public()
            else:
                tenant = SchemaToTenant(schema)
                connection.set_tenant(tenant)
        except:
            connection.set_schema_to_public()
