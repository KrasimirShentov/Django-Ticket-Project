"""
Views for the user-related operations
"""
from rest_framework import (
    generics,
    permissions,
    authentication
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import (
    views,
    status
)

from users.serializers import (
    UserSerializer,
    AuthTokenSerializer
)


class RegisterUserView(generics.CreateAPIView):
    """
    Create (register) a new user in the system.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class CreateTokenView(ObtainAuthToken):
    """
    Create a new auth token for the user.
    """
    serializer_class = AuthTokenSerializer
    permission_classes = (permissions.AllowAny,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LogoutUserView(views.APIView):
    """
    Logout the authenticated user and invalidate their token.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageUserView(generics.RetrieveAPIView):
    """
    Manage the authenticated user.
    """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        Retieve and return authenticated user.
        """
        return self.request.user
