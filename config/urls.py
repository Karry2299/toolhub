from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path

from core.views import index


def health_check(request):
    return JsonResponse({"status": "ok", "app": "ToolHub"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("", include("core.urls")),
]

# Static files are served directly by Nginx in production.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Route Vue client-side pages back to the SPA entry.
urlpatterns += [
    re_path(r"^(?!api/|admin/|static/|media/).*", index, name="spa-catch-all"),
]
