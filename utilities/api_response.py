from botocore.exceptions import EndpointConnectionError
from django.db import transaction
from django.db.utils import IntegrityError, ProgrammingError
from django.http import Http404
from django_tenants.utils import schema_context
from drf_yasg import openapi
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotAuthenticated, ParseError, AuthenticationFailed
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler

from .multitenant.classes import SchemaFromRequest


# from utilities.utililities import notify


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code >= 422:
            return APIFailure(
                status=response.status_code,
                message=exc.detail
            )
    return response


class APISuccess:
    def __new__(cls, message=None, data=None, status=HTTP_200_OK):
        if message and not data:
            return Response(dict(status="success", message=message), status)
        elif data and not message:
            return Response(dict(status="success", data=data), status)
        elif message and data:
            return Response(dict(status="success", message=message, data=data), status)
        else:
            return Response(status=status)


class APIFailure:
    def __new__(cls, message='An error occurred.', status=HTTP_400_BAD_REQUEST):
        return Response(
            {
                'status': 'Failed',
                'message': message
            },
            status
        )


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = {
            'status': renderer_context['response'].status_code < 400,
            'message': data.pop('message'),
            'data': data
        }
        return super(CustomJSONRenderer, self).render(data, accepted_media_type, renderer_context)


def tenant_api_exception(func):
    def inner(self, request, *args, **kwargs):
        try:
            schema = SchemaFromRequest(request)
            with schema_context(schema):
                return check_exceptions(self, func, request, *args, **kwargs)
        except Exception as e:
            print(e, type(e), e.__str__())
            error_msg = e.__str__().split('\n')[0].replace('"', "'")
            return APIFailure(message=error_msg,
                              status=status.HTTP_404_NOT_FOUND if type(e) == Http404 else status.HTTP_400_BAD_REQUEST)

    return inner


def check_errors(field, code, id_s=[], error=None):
    if code == ['does_not_exist']:
        error = f"No {field} with the following IDs {', '.join(id_s)} exists."
    return error


def check_exceptions(self, func, request, *args, **kwargs):
    try:
        with transaction.atomic():
            return func(self, request, *args, **kwargs)
    except ProgrammingError as p:
        return APIFailure(message=p.__str__().split('\n')[0], status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        codes = e.get_codes()
        field = list(e.__dict__['detail'].keys())[0]
        error_is_list = isinstance((e.__dict__['detail'][field]), list)
        if error_is_list:
            error = str(e.__dict__['detail'][field][0])
        else:
            dict__ = e.__dict__['detail'][field]
            keys = list(dict__.keys())[0]
            # detail = dict__[keys]
            error = f"{field} has an invalid input"

        if isinstance(codes[field], list):
            codes = [x for x in codes[field] if x != {}]
            code = codes[0] if len(codes) > 0 else None
            if isinstance(code, list):
                data = e.__dict__['detail'][field]
                id_s = [e.__dict__['detail'][field][_][0].split('"')[1] for _, i in enumerate(data) if i != {}]
                field = field
                if code == ['does_not_exist']:
                    error = f"No {field} with the following IDs ({', '.join(id_s)}) exists."
            if isinstance(code, dict) and code != {}:
                error = f'{list(code.keys())[0]} {code[list(code.keys())[0]][0]}'
        else:
            code = None
        if 'this field' in error:
            error = error.replace("this field", f"that the '{field}' field")
        elif code == 'required':
            error = error.replace('This field', f"The '{field}' field")
        elif code == 'invalid_choice':
            tag = error.split('"')[1]
            rest = error.split('"')[2][:-1]
            error = f"'{tag}'{rest} in the '{field}' field."
        elif code == 'incorrect_type':
            error = error.replace('Incorrect', f"The '{field}' field has an incorrect").replace('pk', 'int')
        elif code == 'does_not_exist':
            pk = error.split('"')[1]
            print(pk, '       pkkkkkkkkk')
            error = f"The {field} with ID '{pk}' does not exist."
        elif code == 'invalid':
            error = error.replace('Invalid', f"The '{field}' field has an invalid"). \
                replace('pk', 'int').replace('a dictionary', 'an object')
        elif code == 'null':
            error = f"The field '{field}' cannot be empty"
        return APIFailure(message=error, status=status.HTTP_400_BAD_REQUEST)
    except ParseError:
        return APIFailure(message="Please check your request data.",
                          status=status.HTTP_400_BAD_REQUEST)
    except NotAuthenticated as e:
        return APIFailure(message=e.detail.__str__(), status=e.status_code)
    except AuthenticationFailed as e:
        return APIFailure(message=e.detail.__str__(), status=e.status_code)
    except EndpointConnectionError as e:
        return APIFailure(message='Unable to connect. Please try again',
                          status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except IntegrityError as e:
        # from general.models import Error
        # schema = SchemaFromRequest(request)
        # if schema != 'public':
        # 	company = SchemaToTenant(schema)
        # 	Error.objects.create(
        # 		error=e.__str__(),
        # 		company=company
        # 	)
        # print(e.__str__())
        if 'Tenant' in e.__str__():
            return APIFailure('This company name is already in use')
        return APIFailure('Duplicate Transaction')
    except Exception as e:
        # from general.models import Error
        # schema = SchemaFromRequest(request)
        # if schema != 'public':
        # 	company = SchemaToTenant(SchemaFromRequest(request))
        # 	Error.objects.create(
        # 		error=e.__str__(),
        # 		company=company
        # 	)
        # print(e.__str__(), type(e))
        error_msg = e.__str__().split('\n')[0].replace('"', "'")
        return APIFailure(message=error_msg,
                          status=status.HTTP_404_NOT_FOUND if type(e) == Http404 else status.HTTP_400_BAD_REQUEST)


def check_ex(exception):
    field = None
    type_ = type(exception)
    if type_ == ProgrammingError:
        error = exception.__str__().split('\n')[0]
    elif type_ == ValidationError:
        e = exception
        codes = e.get_codes()
        field = list(e.__dict__['detail'].keys())[0]
        error_is_list = isinstance((e.__dict__['detail'][field]), list)
        if error_is_list:
            error = str(e.__dict__['detail'][field][0])
        else:
            dict__ = e.__dict__['detail'][field]
            keys = list(dict__.keys())[0]
            # detail = dict__[keys]
            error = f"{field} has an invalid input"

        if isinstance(codes[field], list):
            codes = [x for x in codes[field] if x != {}]
            code = codes[0] if len(codes) > 0 else None
            if isinstance(code, list):
                data = e.__dict__['detail'][field]
                id_s = [e.__dict__['detail'][field][_][0].split('"')[1] for _, i in enumerate(data) if i != {}]
                field = field
                if code == ['does_not_exist']:
                    error = f"No {field} with the following IDs ({', '.join(id_s)}) exists."
            if isinstance(code, dict) and code != {}:
                error = f'{list(code.keys())[0]} {code[list(code.keys())[0]][0]}'
        else:
            code = None
        if 'this field' in error:
            error = error.replace("this field", f"that the '{field}' field")
        elif code == 'required':
            error = error.replace('This field', f"The '{field}' field")
        elif code == 'invalid_choice':
            tag = error.split('"')[1]
            rest = error.split('"')[2][:-1]
            error = f"'{tag}'{rest} in the '{field}' field."
        elif code == 'incorrect_type':
            error = error.replace('Incorrect', f"The '{field}' field has an incorrect").replace('pk', 'int')
        elif code == 'does_not_exist':
            pk = error.split('"')[1]
            error = f"The {field} with ID '{pk}' does not exist."
        elif code == 'invalid':
            error = error.replace('Invalid', f"The '{field}' field has an invalid"). \
                replace('pk', 'int').replace('a dictionary', 'an object')
        elif code == 'null':
            error = f"The field '{field}' cannot be empty"
    elif type_ == ParseError:
        error = "Please check your request data."
    elif type_ == EndpointConnectionError:
        error = 'Unable to connect. Please try again'
    elif type_ == IntegrityError:
        e = exception
        if 'Tenant' in e.__str__():
            error = 'This company name is already in use'
        error = e.__str__()
    elif type_ == KeyError:
        error = exception.__str__().split('\n')[0].replace('"', "'")
        error = f'The field {error} is not in this file '
    else:
        error = exception.__str__().split('\n')[0].replace('"', "'")
    return error, field


def tenant_api(func):
    def inner(self, request, *args, **kwargs):
        schema = SchemaFromRequest(request)
        print(schema)

        if schema == 'public':
            return func(self, request, *args, **kwargs)
        else:
            with schema_context(schema):
                with transaction.atomic():
                    return func(self, request, *args, **kwargs)

    return inner


def api_exception(func):
    def inner(self, request, *args, **kwargs):
        return check_exceptions(self, func, request, *args, **kwargs)

    return inner


def ignore_exception(func):
    def inner(self, request=None, *args, **kwargs):
        try:
            if request is None:
                return func(self, *args, **kwargs)
            return func(self, request, *args, **kwargs)

        except Exception as e:
            pass

    return inner


def action_decorator(fail_silently=True, email=False, notification=False):
    def Inner(func):
        def inner(instance, trigger, schema, automation_id, *args, **kwargs):
            with schema_context(schema):
                with transaction.atomic():
                    try:
                        return func(instance, trigger, schema, automation_id, *args, **kwargs)
                    except Exception as e:
                        # if email or notification:
                        # 	error = check_ex(e)
                        # 	from accounts.models import User
                        # 	from accounts.models import Profile
                        # 	from automation.models import Automation
                        # 	automation = Automation.objects.get(id=automation_id)
                        # 	admin_profile = Profile.objects.filter(name='administrator').first()
                        # 	users = User.objects.filter(Q(profile=admin_profile) & Q(is_active=True))
                        # 	body = f""""
                        # 	The function "{func.__name__.replace("_", " ")}" with trigger "{trigger}" in
                        # 	the automation with name "{automation.name}" and title "{automation.title}",
                        # 	failed to execute due to the following errors:
                        #
                        # 	{error}
                        #
                        # 	Please do well to either supply the correct data or reach out to technical
                        # 	support.
                        # 	"""
                        # 	if notification:
                        # 		notify(users, body=body, title="Action Failed")
                        # 	if email:
                        # 		send_mail(subject='Action Failed', message=body, from_email=settings.EMAIL_HOST_USER,
                        # 				  recipient_list=list(users.values_list('email', flat=True)), fail_silently=True)
                        if not fail_silently:
                            raise e

        return inner

    return Inner


def response_200(schema=None, message="", many=False):
    res = openapi.Response(schema=schema(many=many) if schema is not None else None, description=message)
    return res


def response_400(message):
    res = openapi.Response(description="", examples={
        "application/json": {
            "status": "error",
            "message": message
        }})
    return res
