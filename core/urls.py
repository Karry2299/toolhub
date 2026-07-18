from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"notes", views.NoteViewSet)
router.register(r"todos", views.TodoViewSet)
router.register(r"passwords", views.GeneratedPasswordViewSet)
router.register(r"qrcodes", views.SavedQRCodeViewSet)
router.register(r"ip-lookups", views.IPLookupHistoryViewSet)
router.register(r"tool-usage", views.ToolUsageViewSet)
router.register(r"files", views.UploadedFileViewSet)
router.register(r"clipboard", views.ClipboardItemViewSet)
router.register(r"bookmarks", views.BookmarkViewSet)
router.register(r"reminders", views.ReminderViewSet)
router.register(r"shortlinks", views.ShortLinkViewSet)
router.register(r"expenses", views.ExpenseViewSet)
router.register(r"image-history", views.ImageProcessHistoryViewSet)
router.register(r"image-assets", views.ImageAssetViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", views.api_root, name="api-root"),
    path("api/", include(router.urls)),
    path("api/qrcode/", views.qrcode_api, name="qrcode"),
    path("api/ip-lookup/", views.ip_lookup_api, name="ip-lookup"),
    path("api/password/save/", views.password_save_api, name="password-save"),
    path("api/auth/register/", views.register_api, name="auth-register"),
    path("api/auth/login/", views.login_api, name="auth-login"),
    path("api/auth/me/", views.me_api, name="auth-me"),
    path("api/auth/logout/", views.logout_api, name="auth-logout"),
    path("api/deploy/update/", views.deploy_update_api, name="deploy-update"),
    path("api/server/status/", views.server_status_api, name="server-status"),
    path("api/dashboard/summary/", views.dashboard_summary_api, name="dashboard-summary"),
    path("api/text-tools/log/", views.text_tool_log_api, name="text-tool-log"),
    path("api/image-tools/process/", views.image_process_api, name="image-process"),

    path("api/files/<int:pk>/download/", views.file_download, name="file-download"),
    path("api/files/shared/<uuid:token>/", views.file_share, name="file-share"),
    path("api/filetools/convert/", views.file_convert_api, name="file-convert"),
    path("api/filetools/conversions/", views.file_conversion_list, name="file-conversions"),
    path("s/<slug:code>/", views.shortlink_redirect, name="shortlink-redirect"),

]

