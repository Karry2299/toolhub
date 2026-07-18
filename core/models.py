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
        ("clipboard", "剪贴板"),
        ("bookmark", "书签"),
        ("reminder", "提醒"),
        ("shortlink", "短链接"),
        ("expense", "账本"),
        ("text", "文本工具"),
        ("image", "图片工具"),
    ]
    tool = models.CharField(max_length=30, choices=TOOL_CHOICES, verbose_name="工具")
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
    share_password = models.CharField(max_length=128, blank=True, default="", verbose_name="分享密码")
    share_expires_at = models.DateTimeField(blank=True, null=True, verbose_name="分享过期时间")
    share_max_downloads = models.PositiveIntegerField(default=0, verbose_name="最大下载次数")
    downloads_count = models.IntegerField(default=0, verbose_name="下载次数")
    upload_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="上传IP")
    is_user_deleted = models.BooleanField(default=False, db_index=True, verbose_name="用户已删除")
    user_deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="用户删除时间")
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


class ClipboardItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=120, blank=True, default="", verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    tags = models.CharField(max_length=200, blank=True, default="", verbose_name="标签")
    pinned = models.BooleanField(default=False, verbose_name="置顶")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-pinned", "-updated_at"]
        verbose_name = "剪贴板条目"
        verbose_name_plural = "剪贴板"

    def __str__(self):
        return self.title or self.content[:30]


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=160, verbose_name="标题")
    url = models.URLField(max_length=500, verbose_name="网址")
    category = models.CharField(max_length=80, blank=True, default="", verbose_name="分类")
    note = models.TextField(blank=True, default="", verbose_name="备注")
    open_count = models.PositiveIntegerField(default=0, verbose_name="打开次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["category", "title"]
        verbose_name = "书签"
        verbose_name_plural = "书签管理"

    def __str__(self):
        return self.title


class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=160, verbose_name="标题")
    remind_at = models.DateTimeField(verbose_name="提醒时间")
    repeat = models.CharField(max_length=20, blank=True, default="", verbose_name="重复")
    completed = models.BooleanField(default=False, verbose_name="已完成")
    note = models.TextField(blank=True, default="", verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["completed", "remind_at"]
        verbose_name = "提醒"
        verbose_name_plural = "提醒管理"

    def __str__(self):
        return self.title


class ShortLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    code = models.SlugField(max_length=50, unique=True, verbose_name="短码")
    target_url = models.URLField(max_length=1000, verbose_name="目标网址")
    title = models.CharField(max_length=160, blank=True, default="", verbose_name="标题")
    visits = models.PositiveIntegerField(default=0, verbose_name="访问次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "短链接"
        verbose_name_plural = "短链接管理"

    def __str__(self):
        return self.code


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="金额")
    category = models.CharField(max_length=80, blank=True, default="日常", verbose_name="分类")
    note = models.CharField(max_length=200, blank=True, default="", verbose_name="备注")
    spent_at = models.DateField(verbose_name="日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-spent_at", "-created_at"]
        verbose_name = "账本记录"
        verbose_name_plural = "个人账本"

    def __str__(self):
        return f"{self.category} {self.amount}"


class ImageProcessHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    operation = models.CharField(max_length=30, verbose_name="操作")
    original_name = models.CharField(max_length=255, blank=True, default="", verbose_name="原始文件名")
    result_file = models.FileField(upload_to="image-tools/", blank=True, null=True, verbose_name="结果文件")
    result_text = models.TextField(blank=True, default="", verbose_name="结果文本")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "图片处理记录"
        verbose_name_plural = "图片工具记录"

    def __str__(self):
        return f"{self.operation} - {self.original_name}"


def image_asset_upload_path(instance, filename):
    ext = _os.path.splitext(filename)[1].lower().lstrip(".")
    return f"image-library/{ext or 'misc'}/{filename}"


class ImageAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    image = models.ImageField(upload_to=image_asset_upload_path, verbose_name="图片")
    original_filename = models.CharField(max_length=255, blank=True, default="", verbose_name="原始文件名")
    title = models.CharField(max_length=160, blank=True, default="", verbose_name="标题")
    category = models.CharField(max_length=80, blank=True, default="", verbose_name="分类")
    tags = models.CharField(max_length=200, blank=True, default="", verbose_name="标签")
    is_favorite = models.BooleanField(default=False, verbose_name="收藏")
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小")
    width = models.PositiveIntegerField(default=0, verbose_name="宽度")
    height = models.PositiveIntegerField(default=0, verbose_name="高度")
    content_hash = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="内容哈希")
    is_user_deleted = models.BooleanField(default=False, db_index=True, verbose_name="用户已删除")
    user_deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="用户删除时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "图片素材"
        verbose_name_plural = "图片整理"

    def __str__(self):
        return self.title or self.original_filename


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
        return f"[{self.get_log_type_display()}] {u} @ {self.ip_address}"


class FileConversion(models.Model):
    CONV_TYPES = (
        ("pdf2word", "PDF转Word"),
        ("pdf2txt", "PDF提取文本"),
        ("pdf2images", "PDF转图片"),
        ("merge_pdf", "合并PDF"),
        ("split_pdf", "拆分PDF"),
        ("word2pdf", "Word转PDF"),
        ("excel2csv", "Excel转CSV"),
        ("excel2json", "Excel转JSON"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")
    conv_type = models.CharField(max_length=20, choices=CONV_TYPES, verbose_name="转换类型")
    source_file = models.FileField(upload_to="conversions/input/", verbose_name="源文件")
    result_file = models.FileField(upload_to="conversions/output/", blank=True, null=True, verbose_name="结果文件")
    original_name = models.CharField(max_length=255, blank=True, default="", verbose_name="原始文件名")
    status = models.CharField(max_length=20, default="pending", choices=[
        ("pending", "待处理"), ("processing", "处理中"), ("completed", "已完成"), ("failed", "失败")
    ], verbose_name="状态")
    error_msg = models.TextField(blank=True, default="", verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "文件转换记录"
        verbose_name_plural = "文件转换记录"

    def __str__(self):
        return f"{self.get_conv_type_display()} - {self.original_name}"
