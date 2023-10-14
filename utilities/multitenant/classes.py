from decouple import config

from django.conf import settings
from tenants.models import Hospital, Domain
from tenants.serializer import HospitalSerializer


class CreateTenant:

	def __new__(cls, request):
		tenant_serializer = HospitalSerializer(data=request.data, context=request.data.get('hospital'))
		tenant_serializer.is_valid(raise_exception=True)
		tenant = tenant_serializer.save()
		return tenant


# getters

class SchemaFromRequest:
	def __new__(cls, request, public=settings.DOMAIN, tenant_model=Hospital):
		schema = request.META.get('HTTP_COMPANY')
		if schema is None:
			return "public"

		if (tenant := Hospital.objects.filter(schema_name__iexact=schema).first()):
			return tenant.schema_name
		else:
			raise Exception(f'The hospital "{schema}" does not exist')


class SchemaFromURL:
	def __new__(cls, url):
		url = str(url).replace(':9000', '')
		domain = Domain.objects.filter(domain=url).first()
		if domain is None:
			return 'public'
		return domain.tenant.schema_name


class SchemaToName:
	def __new__(cls, schema: str):
		hospital = Hospital.objects.filter(schema_name=schema).first()
		if hospital is None:
			raise Exception('No hospital with this schema exists')
		return hospital.name


class SchemaToTenant:
	def __new__(cls, schema: str):
		tenant = Hospital.objects.filter(schema_name=schema).first()
		if tenant is None:
			name = SchemaToName(schema)
			raise Exception(f'The hospital: "{name}" does not exist.')
		return tenant


# setters

class NameToUrl:
	def __new__(cls, name: str):
		return f"{config('DOMAIN')}/{name.replace(' ', '-').lower()}"


class NameToSchema:
	def __new__(cls, name: str):
		return name.replace(' ', '_').lower()
