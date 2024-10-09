from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class CustomIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return False

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'jwt':
            return False

        token = parts[1]
        try:
            access_token = AccessToken(token)
            request.user_id = access_token['user_id']
            return True
        except TokenError:
            return False

    def has_object_permission(self, request, view, obj):
        # Optionally, you can include object-level permissions here
        return True