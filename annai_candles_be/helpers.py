from rest_framework import status
from users.choices import UserRoleChoices
from annai_candles_be.common import permission_denied_message
from annai_candles_be.response import api_error_response


def ensure_admin(request):
    if request.user.role != UserRoleChoices.ADMIN:
        return api_error_response(
            permission_denied_message,
            http_status=status.HTTP_403_FORBIDDEN,
        )
    return None