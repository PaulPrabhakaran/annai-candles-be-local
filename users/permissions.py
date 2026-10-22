from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    message = "User account is inactive."
    code = "user_inactive"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)