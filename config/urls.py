from django.contrib import admin
import json
from django.http import JsonResponse
def health_check(request):
    return JsonResponse({"status": "ok", "app": "ToolHub"})
from django.views.generic.base import RedirectView
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('', include('core.urls')),
]

# 闈欐€佹枃浠舵湇鍔?
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 鎶涜锛氭墍鏈?Vue 璺敱閲嶅畾鍚戝埌 SPA
urlpatterns += [
    re_path(r'^(?!/api/|/admin/|/static/|/media/).*', index, name='spa-catch-all'),
]
