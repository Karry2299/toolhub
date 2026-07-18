from threading import Thread

from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin


class AccessLogMiddleware(MiddlewareMixin):
    """Record page visits and API calls."""

    EXCLUDED_PATHS = ["/static/", "/media/", "/favicon"]

    def process_request(self, request):
        path = request.path_info

        if any(path.startswith(prefix) for prefix in self.EXCLUDED_PATHS):
            return

        if not path.startswith("/api/") and path != "/":
            return

        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_address = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else request.META.get("REMOTE_ADDR")
        )

        def log_request():
            try:
                from .models import AccessLog

                user = request.user if hasattr(request, "user") else None
                if isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
                    user = None

                AccessLog.objects.create(
                    log_type="api" if path.startswith("/api/") else "visit",
                    user=user,
                    ip_address=ip_address,
                    path=path,
                    method=request.method,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                )
            except Exception:
                pass

        Thread(target=log_request, daemon=True).start()
