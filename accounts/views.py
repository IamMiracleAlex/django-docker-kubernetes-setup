from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import UserSerializer
from utilities.api_response import tenant_api_exception, APISuccess, tenant_api
from rest_framework.response import Response


hospital = openapi.Parameter('hospital', openapi.IN_HEADER, type=openapi.TYPE_STRING)
authorization = openapi.Parameter('authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING)

class UserAPI(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'delete', 'patch')
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(manual_parameters=[hospital, authorization],
						 operation_summary="Invites a user from an invite key",
						 tags=['user'])
    @tenant_api_exception
    def list(self, request, *args, **kwargs) -> Response:
        data = self.serializer_class(self.get_queryset(), many=True).data
        return APISuccess(data=data)

    @tenant_api_exception
    def retrieve(self, request, *args, **kwargs) -> Response:
        user = self.get_object()
        data = self.serializer_class(user).data
        return APISuccess(data=data)

    @tenant_api_exception
    def delete(self, request, *args, **kwargs) -> Response:
        user = self.get_object()
        user.delete()
        return APISuccess(status=status.HTTP_204_NO_CONTENT)

