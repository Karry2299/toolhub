import ipaddress
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser


class AccessLogMiddleware(MiddlewareMixin):
    """记录所有页面访问日志"""

    EXCLUDED_PATHS = ["/static/", "/media/", "/favicon"]

    def process_request(self, request):
        path = request.path_info

        # 跳过静态文件
        for exc in self.EXCLUDED_PATHS:
            if path.startswith(exc):
                return

        # 只记录页面和API访问
        if not path.startswith("/api/") and not path == "/":
            return

        # 获取真实IP
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

        # 异步写入日志（避免阻塞请求）
        from threading import Thread
        from .models import AccessLog

        def _log():
            try:
                user = request.user if hasattr(request, "user") and not isinstance(request.user, AnonymousUser) else None
                AccessLog.objects.create(
                    log_type="api" if path.startswith("/api/") else "visit",
                    user=user if user and user.is_authenticated else None,
                    ip_address=ip,
                    path=path,
                    method=request.method,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                )
            except:
                pass

        Thread(target=_log, daemon=True).start()
