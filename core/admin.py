from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import (
    AccessLog, Bookmark, ClipboardItem, Expense, FileConversion,
    GeneratedPassword, ImageAsset, ImageProcessHistory, IPLookupHistory, Note, Reminder,
    SavedQRCode, ShortLink, Todo, ToolUsage, UploadedFile,
)


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ["log_type_icon", "user", "ip_address", "path", "method", "created_at"]
    list_filter = ["log_type", "created_at"]
    search_fields = ["ip_address", "path", "user__username", "detail"]
    date_hierarchy = "created_at"
    readonly_fields = ["log_type", "user", "ip_address", "path", "method", "user_agent", "detail", "created_at"]
    list_per_page = 50

    def log_type_icon(self, obj):
        icons = {"visit": "\U0001f310", "login": "\U0001f511", "upload": "\U0001f4e4", "api": "\u26a1"}
        return f"{icons.get(obj.log_type, '\U0001f4dd')} {obj.get_log_type_display()}"
    log_type_icon.short_description = "\u7c7b\u578b"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(FileConversion)
class FileConversionAdmin(admin.ModelAdmin):
    list_display = ["conv_type", "user", "original_name", "status", "created_at"]
    list_filter = ["conv_type", "status", "created_at"]
    search_fields = ["original_name", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    readonly_fields = ["source_file", "result_file", "original_name", "status", "error_msg", "created_at"]


@admin.register(ClipboardItem)
class ClipboardItemAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "tags", "pinned", "updated_at"]
    list_filter = ["pinned", "updated_at"]
    search_fields = ["title", "content", "tags", "user__username"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "user", "open_count", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "url", "note", "user__username"]
    raw_id_fields = ["user"]
    readonly_fields = ["open_count", "created_at"]


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "remind_at", "repeat", "completed", "created_at"]
    list_filter = ["completed", "repeat", "remind_at"]
    search_fields = ["title", "note", "user__username"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "user", "visits", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["code", "target_url", "title", "user__username"]
    raw_id_fields = ["user"]
    readonly_fields = ["visits", "created_at"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["category", "amount", "user", "spent_at", "created_at"]
    list_filter = ["category", "spent_at"]
    search_fields = ["category", "note", "user__username"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]


@admin.register(ImageProcessHistory)
class ImageProcessHistoryAdmin(admin.ModelAdmin):
    list_display = ["operation", "original_name", "user", "created_at"]
    list_filter = ["operation", "created_at"]
    search_fields = ["operation", "original_name", "user__username"]
    raw_id_fields = ["user"]
    readonly_fields = ["operation", "original_name", "result_file", "result_text", "created_at"]


@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ["original_filename", "title", "category", "user", "is_favorite", "is_user_deleted", "user_deleted_at", "width", "height", "file_size", "updated_at"]
    list_filter = ["category", "is_favorite", "is_user_deleted", "user_deleted_at", "updated_at"]
    search_fields = ["original_filename", "title", "category", "tags", "user__username", "content_hash"]
    raw_id_fields = ["user"]
    readonly_fields = ["original_filename", "file_size", "width", "height", "content_hash", "is_user_deleted", "user_deleted_at", "created_at", "updated_at"]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["title", "content", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    fieldsets = [
        ("基本信息", {"fields": ["user", "title"]}),
        ("内容", {"fields": ["content"]}),
        ("时间信息", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "completed", "created_at"]
    list_filter = ["completed", "created_at"]
    search_fields = ["title", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    list_editable = ["completed"]
    fieldsets = [
        ("基本信息", {"fields": ["user", "title", "completed"]}),
        ("时间信息", {"fields": ["created_at"], "classes": ["collapse"]}),
    ]
    readonly_fields = ["created_at"]


@admin.register(GeneratedPassword)
class GeneratedPasswordAdmin(admin.ModelAdmin):
    list_display = ["password_short", "user", "length", "note_short", "created_at"]
    list_filter = ["length", "has_upper", "has_lower", "has_digits", "has_symbols", "created_at"]
    search_fields = ["password", "note", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]

    def password_short(self, obj):
        return obj.password[:30] + "..." if len(obj.password) > 30 else obj.password
    password_short.short_description = "密码"

    def note_short(self, obj):
        return obj.note[:20] + "..." if len(obj.note) > 20 else (obj.note or "-")
    note_short.short_description = "备注"


@admin.register(SavedQRCode)
class SavedQRCodeAdmin(admin.ModelAdmin):
    list_display = ["content_short", "user", "size", "created_at"]
    list_filter = ["size", "created_at"]
    search_fields = ["content", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]

    def content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_short.short_description = "二维码内容"


@admin.register(IPLookupHistory)
class IPLookupHistoryAdmin(admin.ModelAdmin):
    list_display = ["query", "ip", "country", "region", "city", "user", "created_at"]
    list_filter = ["country", "region", "city", "created_at"]
    search_fields = ["query", "ip", "country", "region", "city", "org", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]
    fieldsets = [
        ("查询信息", {"fields": ["user", "query", "ip"]}),
        ("位置信息", {"fields": ["country", "region", "city", "org"]}),
        ("时间信息", {"fields": ["created_at"], "classes": ["collapse"]}),
    ]


@admin.register(ToolUsage)
class ToolUsageAdmin(admin.ModelAdmin):
    list_display = ["tool_display", "action", "user", "detail_short", "created_at"]
    list_filter = ["tool", "action", "created_at"]
    search_fields = ["detail", "user__username"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]

    def tool_display(self, obj):
        return obj.get_tool_display()
    tool_display.short_description = "工具"
    tool_display.admin_order_field = "tool"

    def detail_short(self, obj):
        return obj.detail[:30] + "..." if len(obj.detail) > 30 else (obj.detail or "-")
    detail_short.short_description = "详情"


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ["original_filename", "user", "file_size_display", "file_type_display", "is_favorite", "is_user_deleted", "user_deleted_at", "downloads_count", "uploaded_at"]
    list_filter = ["is_favorite", "is_user_deleted", "user_deleted_at", "file_type", "uploaded_at"]
    search_fields = ["original_filename", "user__username"]
    date_hierarchy = "uploaded_at"
    raw_id_fields = ["user"]
    readonly_fields = ["file_size", "share_token", "downloads_count", "is_user_deleted", "user_deleted_at", "uploaded_at"]
    list_display_links = ["original_filename"]
    list_per_page = 20

    def file_size_display(self, obj):
        s = obj.file_size
        if s < 1024: return f"{s}B"
        if s < 1024**2: return f"{s/1024:.1f}KB"
        return f"{s/1024**2:.1f}MB"
    file_size_display.short_description = "大小"

    def file_type_display(self, obj):
        t = obj.file_type or ""
        if t.startswith("image/"): return "图片"
        if t.startswith("video/"): return "视频"
        if t.startswith("audio/"): return "音频"
        if "pdf" in t: return "PDF"
        if "zip" in t or "rar" in t: return "压缩包"
        return "其他"
    file_type_display.short_description = "类型"


class DeployAdminView(admin.AdminSite):
    pass


def deploy_view(request):
    """一键更新页面"""
    context = {
        "title": "一键部署更新",
        "site_title": admin.site.site_title,
        "site_header": admin.site.site_header,
    }
    return TemplateResponse(request, "admin/deploy.html", context)


def deploy_ajax(request):
    """AJAX 触发更新"""
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "message": "无权限"}, status=403)

    if request.method == "POST":
        try:
            from django.core.management import call_command
            from django.core.management.base import CommandError
            from io import StringIO

            out = StringIO()
            err = StringIO()
            try:
                call_command("deploy_update", stdout=out, stderr=err)
                return JsonResponse({"success": True, "message": "更新成功", "output": out.getvalue(), "error": err.getvalue()})
            except CommandError as e:
                return JsonResponse({"success": False, "message": str(e), "output": out.getvalue(), "error": err.getvalue()})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "仅支持 POST"}, status=405)
