from rest_framework import serializers
from .models import Note, Todo, GeneratedPassword, SavedQRCode, IPLookupHistory, ToolUsage, UploadedFile


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
        fields = ["id", "user", "file", "original_filename", "file_size", "file_type",
                  "size_display", "file_icon", "is_favorite", "share_token",
                  "downloads_count", "download_url", "uploaded_at"]
        read_only_fields = ["user", "original_filename", "file_size", "file_type",
                            "share_token", "downloads_count", "uploaded_at"]

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
        if request:
            return request.build_absolute_uri(f"/api/files/{obj.pk}/download/")
        return f"/api/files/{obj.pk}/download/"