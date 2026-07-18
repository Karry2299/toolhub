from rest_framework import serializers
from .models import (
    Bookmark, ClipboardItem, Expense, GeneratedPassword, ImageProcessHistory,
    ImageAsset, IPLookupHistory, Note, Reminder, SavedQRCode, ShortLink, Todo, ToolUsage,
    UploadedFile,
)


class NoteSerializer(serializers.ModelSerializer):
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ["id", "user", "title", "content", "preview", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_preview(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["id", "user", "title", "completed", "created_at"]
        read_only_fields = ["user", "created_at"]


class GeneratedPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPassword
        fields = ["id", "user", "password", "length", "has_upper", "has_lower",
                  "has_digits", "has_symbols", "note", "created_at"]
        read_only_fields = ["user", "created_at"]


class SavedQRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedQRCode
        fields = ["id", "user", "content", "size", "created_at"]
        read_only_fields = ["user", "created_at"]


class IPLookupHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLookupHistory
        fields = ["id", "user", "query", "ip", "country", "region", "city", "org", "created_at"]
        read_only_fields = ["user", "created_at"]


class ToolUsageSerializer(serializers.ModelSerializer):
    tool_display = serializers.SerializerMethodField()

    class Meta:
        model = ToolUsage
        fields = ["id", "user", "tool", "tool_display", "action", "detail", "created_at"]
        read_only_fields = ["user", "created_at"]

    def get_tool_display(self, obj):
        return obj.get_tool_display()


class UploadedFileSerializer(serializers.ModelSerializer):
    size_display = serializers.SerializerMethodField()
    file_icon = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = ["id", "user", "file", "original_filename", "file_size", "file_type", "upload_ip",
                  "size_display", "file_icon", "is_favorite", "share_token",
                  "share_password", "share_expires_at", "share_max_downloads",
                  "downloads_count", "is_user_deleted", "user_deleted_at", "download_url", "uploaded_at"]
        read_only_fields = ["user", "original_filename", "file_size", "file_type",
                            "share_token", "downloads_count", "is_user_deleted", "user_deleted_at", "uploaded_at"]

    def get_size_display(self, obj):
        s = obj.file_size
        if s < 1024:
            return f"{s}B"
        if s < 1024 ** 2:
            return f"{s / 1024:.1f}KB"
        return f"{s / 1024 ** 2:.1f}MB"

    def get_file_icon(self, obj):
        t = obj.file_type or ""
        if t.startswith("image/"): return "🖼"
        if t.startswith("video/"): return "🎬"
        if t.startswith("audio/"): return "🎵"
        if "pdf" in t: return "📄"
        if "zip" in t or "rar" in t or "tar" in t: return "📦"
        return "📎"

    def get_download_url(self, obj):
        request = self.context.get("request")
        path = f"/api/files/shared/{obj.share_token}/"
        if request:
            return request.build_absolute_uri(path)
        return path


class ClipboardItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClipboardItem
        fields = ["id", "user", "title", "content", "tags", "pinned", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ["id", "user", "title", "url", "category", "note", "open_count", "created_at"]
        read_only_fields = ["user", "open_count", "created_at"]


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["id", "user", "title", "remind_at", "repeat", "completed", "note", "created_at"]
        read_only_fields = ["user", "created_at"]


class ShortLinkSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    code = serializers.SlugField(max_length=50, required=False, allow_blank=True)

    class Meta:
        model = ShortLink
        fields = ["id", "user", "code", "target_url", "title", "visits", "short_url", "created_at"]
        read_only_fields = ["user", "visits", "short_url", "created_at"]

    def get_short_url(self, obj):
        request = self.context.get("request")
        path = f"/s/{obj.code}/"
        if request:
            return request.build_absolute_uri(path)
        return path


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "user", "amount", "category", "note", "spent_at", "created_at"]
        read_only_fields = ["user", "created_at"]


class ImageProcessHistorySerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageProcessHistory
        fields = ["id", "user", "operation", "original_name", "result_file", "result_text", "download_url", "created_at"]
        read_only_fields = ["user", "original_name", "result_file", "result_text", "created_at"]

    def get_download_url(self, obj):
        if not obj.result_file:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.result_file.url)
        return obj.result_file.url


class ImageAssetSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    size_display = serializers.SerializerMethodField()
    duplicate_count = serializers.SerializerMethodField()

    class Meta:
        model = ImageAsset
        fields = [
            "id", "user", "image", "image_url", "original_filename", "title",
            "category", "tags", "is_favorite", "file_size", "size_display",
            "width", "height", "content_hash", "duplicate_count",
            "is_user_deleted", "user_deleted_at", "created_at", "updated_at",
        ]
        read_only_fields = [
            "user", "original_filename", "file_size", "width", "height",
            "content_hash", "is_user_deleted", "user_deleted_at", "created_at", "updated_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_size_display(self, obj):
        s = obj.file_size
        if s < 1024:
            return f"{s}B"
        if s < 1024 ** 2:
            return f"{s / 1024:.1f}KB"
        return f"{s / 1024 ** 2:.1f}MB"

    def get_duplicate_count(self, obj):
        if not obj.content_hash:
            return 0
        return ImageAsset.objects.filter(user=obj.user, content_hash=obj.content_hash).exclude(pk=obj.pk).count()
