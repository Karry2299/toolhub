from django.contrib import admin
from .models import Note, Todo, GeneratedPassword, SavedQRCode, IPLookupHistory, ToolUsage, UploadedFile


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
    list_display = ["original_filename", "user", "file_size_display", "file_type_display", "is_favorite", "downloads_count", "uploaded_at"]
    list_filter = ["is_favorite", "file_type", "uploaded_at"]
    search_fields = ["original_filename", "user__username"]
    date_hierarchy = "uploaded_at"
    raw_id_fields = ["user"]
    readonly_fields = ["file_size", "share_token", "downloads_count", "uploaded_at"]
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