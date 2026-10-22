from users.models import UserLoginActivity

def get_client_ip(request):
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def record_login_logout_activity(
    request, user, activity_type
):
    user_agent = request.META.get("HTTP_USER_AGENT", "") or ""
    UserLoginActivity.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=get_client_ip(request),
        user_agent=user_agent[:1000],
    )