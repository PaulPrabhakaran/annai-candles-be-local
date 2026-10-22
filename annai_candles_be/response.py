from rest_framework import status
from rest_framework.response import Response
from annai_candles_be.common import permission_denied_message, custom_error_message

_UNSET = object()


def api_response(message, data=_UNSET, http_status=status.HTTP_200_OK, extra=None):
    payload = {"message": message}
    if data is not _UNSET:
        payload["data"] = data
    if extra:
        payload.update(extra)
    return Response(payload, status=http_status)


def api_error_response(message, http_status=status.HTTP_400_BAD_REQUEST, data=_UNSET, extra=None):
    return api_response(message, data=data, http_status=http_status, extra=extra)



def _extract_message(detail):
    """
    Return the first readable message from any DRF error structure:
    str, list, dict, nested dict, or list of dicts (many=True).
    Returns None if no message is found.
    """
    if isinstance(detail, dict):
        if "message" in detail:
            return _extract_message(detail["message"])
        for value in detail.values():
            message = _extract_message(value)
            if message:
                return message
        return None

    if isinstance(detail, (list, tuple)):
        for item in detail:
            message = _extract_message(item)
            if message:
                return message
        return None

    return str(detail) if detail not in (None, "") else None


def frontend_error_response(error):
    """
    Accepts:
      - an APIException / ValidationError (uses .detail)
      - raw serializer.errors (dict / list)
      - any other exception (falls back to str(error))
    """
    detail = getattr(error, "detail", error)

    message = (
        _extract_message(detail)
        or str(error)
        or custom_error_message
    )

    http_status = (
        status.HTTP_403_FORBIDDEN
        if message == permission_denied_message
        else status.HTTP_400_BAD_REQUEST
    )

    return api_error_response(message, http_status=http_status)
