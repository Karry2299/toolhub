from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    title = models.CharField(max_length=200, blank=True, default="", verbose_name="标题")
    content = models.TextField(blank=True, default="", verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "笔记"
        verbose_name_plural = "笔记管理"

    def __str__(self):
        return self.title or "无标题"


class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    title = models.CharField(max_length=200, verbose_name="任务内容")
    completed = models.BooleanField(default=False, verbose_name="已完成")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["completed", "-created_at"]
        verbose_name = "待办事项"
        verbose_name_plural = "待办事项管理"

    def __str__(self):
        return self.title


class GeneratedPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    password = models.CharField(max_length=128, verbose_name="密码")
    length = models.IntegerField(verbose_name="密码长度")
    has_upper = models.BooleanField(default=True, verbose_name="包含大写字母")
    has_lower = models.BooleanField(default=True, verbose_name="包含小写字母")
    has_digits = models.BooleanField(default=True, verbose_name="包含数字")
    has_symbols = models.BooleanField(default=True, verbose_name="包含特殊字符")
    note = models.TextField(blank=True, default="", verbose_name="备注说明")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "生成的密码"
        verbose_name_plural = "密码管理"

    def __str__(self):
        if self.note:
            return self.note[:30]
        return f"{self.password[:20]}..."


class SavedQRCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    content = models.TextField(verbose_name="二维码内容")
    size = models.IntegerField(default=200, verbose_name="尺寸")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "保存的二维码"
        verbose_name_plural = "二维码管理"

    def __str__(self):
        return self.content[:50]


class IPLookupHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    query = models.CharField(max_length=200, verbose_name="查询内容")
    ip = models.CharField(max_length=50, blank=True, verbose_name="IP地址")
    country = models.CharField(max_length=100, blank=True, verbose_name="国家")
    region = models.CharField(max_length=100, blank=True, verbose_name="省份")
    city = models.CharField(max_length=100, blank=True, verbose_name="城市")
    org = models.CharField(max_length=200, blank=True, verbose_name="运营商")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="查询时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "IP查询记录"
        verbose_name_plural = "IP查询记录管理"

    def __str__(self):
        return f"{self.query} -> {self.ip}"


class ToolUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    TOOL_CHOICES = [
        ("notes", "在线笔记"),
        ("todo", "待办事项"),
        ("password", "密码生成器"),
        ("qrcode", "二维码"),
        ("ip", "IP查询"),
        ("file", "文件管理"),
    ]
    tool = models.CharField(max_length=20, choices=TOOL_CHOICES, verbose_name="工具")
    action = models.CharField(max_length=50, default="use", verbose_name="操作")
    detail = models.CharField(max_length=500, blank=True, default="", verbose_name="详情")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="使用时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "工具使用记录"
        verbose_name_plural = "使用统计"

    def __str__(self):
        return f"{self.get_tool_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


import uuid
import os as _os


def file_upload_path(instance, filename):
    ext = _os.path.splitext(filename)[1].lower().lstrip(".")
    return f"uploads/{ext or 'misc'}/{filename}"


class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    file = models.FileField(upload_to=file_upload_path, verbose_name="文件")
    original_filename = models.CharField(max_length=255, blank=True, default="", verbose_name="原始文件名")
    file_size = models.BigIntegerField(default=0, editable=False, verbose_name="文件大小")
    file_type = models.CharField(max_length=100, blank=True, default="", verbose_name="文件类型")
    is_favorite = models.BooleanField(default=False, verbose_name="是否收藏")
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="分享令牌")
    downloads_count = models.IntegerField(default=0, verbose_name="下载次数")
    upload_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="上传IP")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "上传的文件"
        verbose_name_plural = "文件管理"

    def __str__(self):
        return self.original_filename

    def filename_display(self):
        return self.original_filename[:50]
    filename_display.short_description = "文件名"

    def size_display(self):
        s = self.file_size
        if s < 1024:
            return f"{s}B"
        if s < 1024 ** 2:
            return f"{s / 1024:.1f}KB"
        return f"{s / 1024 ** 2:.1f}MB"
    size_display.short_description = "大小"

    def file_icon(self):
        t = self.file_type or ""
        if t.startswith("image/"):
            return "🖼"
        if t.startswith("video/"):
            return "🎬"
        if t.startswith("audio/"):
            return "🎵"
        if "pdf" in t:
            return "📄"
        if "zip" in t or "rar" in t or "tar" in t:
            return "📦"
        return "📎"


class AccessLog(models.Model):
    LOG_TYPES = (
        ("visit", "页面访问"),
        ("login", "用户登录"),
        ("upload", "文件上传"),
        ("api", "API调用"),
    )
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, db_index=True, verbose_name="日志类型")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="用户")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP地址")
    path = models.CharField(max_length=500, blank=True, default="", verbose_name="访问路径")
    method = models.CharField(max_length=10, blank=True, default="", verbose_name="请求方法")
    user_agent = models.TextField(blank=True, default="", verbose_name="用户代理")
    detail = models.CharField(max_length=500, blank=True, default="", verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "访问日志"
        verbose_name_plural = "访问日志"

    def __str__(self):
        u = self.user.username if self.user else "匿名"
        return f"[{self.get_log_type_display()}] {u} @ {self.ip_address}";

# Add upload_ip to UploadedFile

        file_icon.short_description = "类型"