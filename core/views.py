import io
import json
import subprocess
import sys
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets
from .models import Note, Todo, GeneratedPassword, SavedQRCode, IPLookupHistory, ToolUsage, FileConversion
from .serializers import (NoteSerializer, TodoSerializer, UploadedFileSerializer, GeneratedPasswordSerializer,
                          SavedQRCodeSerializer, IPLookupHistorySerializer, ToolUsageSerializer)

def index(request):
    index_path = settings.BASE_DIR / 'static' / 'vue' / 'index.html'
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')

def api_root(request):
    return JsonResponse({
        "name": "ToolHub API",
        "version": "1.0",
        "endpoints": {
            "auth": {"register": "/api/auth/register/", "login": "/api/auth/login/", "me": "/api/auth/me/", "logout": "/api/auth/logout/"},
            "notes": "/api/notes/", "todos": "/api/todos/", "passwords": "/api/passwords/",
            "qrcodes": "/api/qrcodes/", "ip_lookups": "/api/ip-lookups/", "files": "/api/files/",
            "tools": {"qrcode": "/api/qrcode/?text=...", "ip_lookup": "/api/ip-lookup/?q=..."},
        },
    })

    return HttpResponse('Frontend is building...', content_type='text/html')

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.none()
    serializer_class = NoteSerializer
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, upload_ip=_get_client_ip(self.request))

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.none()
    serializer_class = TodoSerializer
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GeneratedPasswordViewSet(viewsets.ModelViewSet):
    queryset = GeneratedPassword.objects.none()
    serializer_class = GeneratedPasswordSerializer
    def get_queryset(self):
        return GeneratedPassword.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SavedQRCodeViewSet(viewsets.ModelViewSet):
    queryset = SavedQRCode.objects.none()
    serializer_class = SavedQRCodeSerializer
    def get_queryset(self):
        return SavedQRCode.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IPLookupHistoryViewSet(viewsets.ModelViewSet):
    queryset = IPLookupHistory.objects.none()
    serializer_class = IPLookupHistorySerializer
    def get_queryset(self):
        return IPLookupHistory.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ToolUsageViewSet(viewsets.ModelViewSet):
    queryset = ToolUsage.objects.none()
    serializer_class = ToolUsageSerializer
    def get_queryset(self):
        return ToolUsage.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def qrcode_api(request):
    try:
        import qrcode
        from PIL import Image
        text = request.GET.get('text', '')
        size = int(request.GET.get('size', 200))
        save = request.GET.get('save', '0')
        if not text:
            return JsonResponse({'error': '\u8bf7\u63d0\u4f9btext \u53c2\u6570'}, status=400)
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        img = img.resize((size, size), Image.NEAREST)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        if save == '1':
            SavedQRCode.objects.create(content=text, size=size)
            ToolUsage.objects.create(tool='qrcode', action='generate', detail=text[:100])
        return HttpResponse(buf.getvalue(), content_type='image/png')
    except ImportError:
        return JsonResponse({'error': 'QRCode library not installed'}, status=500)

def ip_lookup_api(request):
    q = request.GET.get('q', '')
    save = request.GET.get('save', '0')
    if not q:
        return JsonResponse({'error': '\u8bf7\u63d0\u4f9bq \u53c2\u6570'}, status=400)
    try:
        r = requests.get(f'http://ip-api.com/json/{q}', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            result = {
                'ip': data.get('query', ''),
                'country': data.get('country', ''),
                'region': data.get('regionName', ''),
                'city': data.get('city', ''),
                'org': data.get('isp', '') or data.get('org', ''),
            }
            if save == '1':
                IPLookupHistory.objects.create(query=q, **result)
                ToolUsage.objects.create(tool='ip', action='lookup', detail=q)
            return JsonResponse(result)
        else:
            return JsonResponse({'error': data.get('message', '\u67e5\u8be2\u5931\u8d25')}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def password_save_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pwd = data.get('password', '')
            length = data.get('length', 0)
            note = data.get('note', '')
            pwd_obj = GeneratedPassword.objects.create(
                password=pwd, length=length, note=note,
                has_upper=data.get('has_upper', False),
                has_lower=data.get('has_lower', False),
                has_digits=data.get('has_digits', False),
                has_symbols=data.get('has_symbols', False),
            )
            ToolUsage.objects.create(tool='password', action='generate')
            return JsonResponse({'id': pwd_obj.id, 'password': pwd_obj.password, 'note': pwd_obj.note,
                                 'created_at': pwd_obj.created_at.isoformat()})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)

import mimetypes
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import UploadedFile
from .serializers import UploadedFileSerializer

class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.none()
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        if file_obj:
            serializer.save(
                user=self.request.user,
                original_filename=file_obj.name,
                file_size=file_obj.size,
                file_type=file_obj.content_type or '',
            )
        else:
            serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        file_obj = self.get_object()
        file_obj.is_favorite = not file_obj.is_favorite
        file_obj.save(update_fields=['is_favorite'])
        return JsonResponse({'is_favorite': file_obj.is_favorite})

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        qs = UploadedFile.objects.filter(is_favorite=True)
        serializer = self.get_serializer(qs, many=True)
        return JsonResponse(serializer.data, safe=False)

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
def _get_client_ip(request):
    """获取客户端真实IP"""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")




@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '')
        if not username or not password:
            return JsonResponse({'error': '\u7528\u6237\u540d\u548c\u5bc6\u7801\u4e0d\u80fd\u4e3a\u7a7a'}, status=400)
        if len(password) < 6:
            return JsonResponse({'error': '\u5bc6\u7801\u81f3\u5c11\u97006\u4f4d'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '\u7528\u6237\u540d\u5df2\u5b58\u5728'}, status=400)
        user = User.objects.create_user(username=username, password=password, email=email)
        token, _ = Token.objects.get_or_create(user=user)
        # 记录登录日志
        try:
            from .models import AccessLog
            AccessLog.objects.create(
                log_type="login", user=user,
                ip_address=_get_client_ip(request),
                path="/api/auth/login/", method="POST",
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                detail=f"用户 {user.username} 登录"
            )
        except:
            pass
        return JsonResponse({'token': token.key, 'username': user.username, 'user_id': user.id, 'is_superuser': user.is_superuser})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key, 'username': user.username, 'user_id': user.id, 'is_superuser': user.is_superuser})
        return JsonResponse({'error': '\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
def me_api(request):
    token_key = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
    try:
        token = Token.objects.get(key=token_key)
        return JsonResponse({'username': token.user.username, 'user_id': token.user.id, 'is_superuser': token.user.is_superuser})
    except Token.DoesNotExist:
        return JsonResponse({'error': '\u672a\u767b\u5f55'}, status=401)

@api_view(['POST'])
def logout_api(request):
    try:
        request.user.auth_token.delete()
        return JsonResponse({'message': '\u5df2\u9000\u51fa'})
    except:
        return JsonResponse({'message': 'OK'})

def file_download(request, pk):
    file_obj = get_object_or_404(UploadedFile, pk=pk)
    file_obj.downloads_count += 1
    file_obj.save(update_fields=['downloads_count'])
    response = FileResponse(file_obj.file, as_attachment=True, filename=file_obj.original_filename)
    return response

def file_share(request, token):
    """分享链接直接下载文件"""
    file_obj = get_object_or_404(UploadedFile, share_token=token)
    file_obj.downloads_count += 1
    file_obj.save(update_fields=["downloads_count"])
    response = FileResponse(file_obj.file, as_attachment=True, filename=file_obj.original_filename)
    return response
@api_view(["GET"])
def server_status_api(request):
    """服务器状态（仅管理员可见）"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({"error": "无权限"}, status=403)
    try:
        import json, subprocess, shutil
        # 磁盘信息
        disk_total = disk_used = disk_percent = 0
        try:
            du = shutil.disk_usage("/")
            disk_total = round(du.total / (1024**3), 1)
            disk_used = round(du.used / (1024**3), 1)
            disk_percent = round(du.used / du.total * 100, 1)
        except:
            pass
        
        # 内存信息
        mem_total = mem_used = mem_percent = 0
        try:
            r = subprocess.run(["free", "-b"], capture_output=True, text=True, timeout=5)
            for ln in r.stdout.split(chr(10)):
                if ln.startswith("Mem:"):
                    parts = ln.split()
                    if len(parts) >= 3:
                        mem_total = int(parts[1])
                        mem_used = int(parts[2])
                        mem_percent = round(mem_used / mem_total * 100, 1) if mem_total > 0 else 0
        except:
            pass
        
        # CPU 信息（使用 /proc/stat 更可靠）
        cpu_percent = 0
        try:
            with open("/proc/stat") as f:
                line = f.readline()
            parts = line.strip().split()
            if len(parts) >= 5:
                values = [int(x) for x in parts[1:]]
                total = sum(values)
                idle = values[3]
                if total > 0:
                    cpu_percent = round((1 - idle / total) * 100, 1)
        except:
            pass

        # 统计网站访问次数
        try:
            from .models import AccessLog
            visit_count = AccessLog.objects.filter(log_type="visit").count()
            user_count = AccessLog.objects.filter(log_type="visit").values("ip_address").distinct().count()
        except:
            visit_count = 0
            user_count = 0

        
        return JsonResponse({
            "disk": {"total": disk_total, "used": disk_used, "free": round(disk_total - disk_used, 1), "percent": disk_percent},
            "memory": {"total": mem_total, "used": mem_used, "percent": mem_percent},
            "cpu": {"percent": cpu_percent}, "visits": {"total": visit_count, "unique_ips": user_count},
        })
    except Exception as e:
        return JsonResponse({"error": str(e), "detail": "服务器状态获取失败"}, status=500)


@api_view(["POST"])
@api_view(["POST"])
def deploy_update_api(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({"error": "无权限"}, status=403)
    try:
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        err = StringIO()
        old_out = sys.stdout
        old_err = sys.stderr
        sys.stdout = out
        sys.stderr = err
        try:
            call_command("deploy_update")
            success = True
            msg = "更新完成"
        except SystemExit as e:
            success = False
            msg = f"更新失败 (code {e.code})"
        finally:
            sys.stdout = old_out
            sys.stderr = old_err
        return JsonResponse({
            "success": success, "message": msg,
            "output": out.getvalue(), "error": err.getvalue()
        }, status=200 if success else 500)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)




# ===== 文件转换处理 =====
import os as _os
import csv
import json as _json
from io import BytesIO
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt

def _get_file_path(relative_path):
    return _os.path.join(settings.MEDIA_ROOT, relative_path)

@csrf_exempt
def file_convert_api(request):
    """文件转换统一入口"""
    if request.method != "POST":
        return JsonResponse({"error": "\u4ec5\u652f\u6301POST"}, status=405)
    conv_type = request.POST.get("conv_type", "")
    upload = request.FILES.get("file")
    if not conv_type:
        return JsonResponse({"error": "\u8bf7\u6307\u5b9a\u8f6c\u6362\u7c7b\u578b"}, status=400)
    if not upload:
        return JsonResponse({"error": "\u8bf7\u4e0a\u4f20\u6587\u4ef6"}, status=400)
    try:
        rec = FileConversion(user=request.user if request.user.is_authenticated else None)
        rec.conv_type = conv_type
        rec.original_name = upload.name
        rec.status = "processing"
        rec.source_file.save(upload.name, upload, save=True)
        if conv_type == "pdf2word":
            result = _convert_pdf_to_word(rec)
        elif conv_type == "pdf2txt":
            result = _convert_pdf_to_text(rec)
        elif conv_type == "pdf2images":
            result = _convert_pdf_to_images(rec)
        elif conv_type == "merge_pdf":
            result = _merge_pdfs([rec])
        elif conv_type == "split_pdf":
            page = request.POST.get("page", "1")
            result = _split_pdf(rec, page)
        elif conv_type == "word2pdf":
            result = _convert_word_to_pdf(rec)
        elif conv_type == "excel2csv":
            result = _convert_excel_to_csv(rec)
        elif conv_type == "excel2json":
            result = _convert_excel_to_json(rec)
        else:
            return JsonResponse({"error": f"\u4e0d\u652f\u6301\u7684\u8f6c\u6362\u7c7b\u578b: {conv_type}"}, status=400)
        rec.status = "completed"
        if result.get("path"):
            rec.result_file = result["path"]
        rec.save()
        ToolUsage.objects.create(user=request.user if request.user.is_authenticated else None, tool="file", action=conv_type, detail=f"\u6587\u4ef6\u8f6c\u6362: {conv_type}")
        return JsonResponse({"success": True, "message": result.get("message", "\u8f6c\u6362\u6210\u529f"), "filename": result.get("filename", ""), "download_url": result.get("download_url", "")})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def _convert_pdf_to_word(rec):
    from pdf2docx import Converter
    input_path = rec.source_file.path
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    output_name = f"{base}.docx"
    output_rel = f"conversions/output/{output_name}"
    output_path = _os.path.join(settings.MEDIA_ROOT, output_rel)
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return {"message": "PDF \u5df2\u8f6c\u6362\u4e3a Word", "filename": output_name, "path": output_rel, "download_url": f"{settings.MEDIA_URL}{output_rel}"}

def _convert_pdf_to_text(rec):
    import fitz
    input_path = rec.source_file.path
    doc = fitz.open(input_path)
    text = ""
    for page in doc: text += page.get_text() + "\n"
    doc.close()
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    output_name = f"{base}.txt"
    output_rel = f"conversions/output/{output_name}"
    output_path = _os.path.join(settings.MEDIA_ROOT, output_rel)
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f: f.write(text)
    return {"message": f"\u5df2\u63d0\u53d6\u6587\u672c ({len(text)} \u5b57\u7b26)", "filename": output_name, "path": output_rel, "download_url": f"{settings.MEDIA_URL}{output_rel}"}

def _convert_pdf_to_images(rec):
    import fitz; import zipfile
    input_path = rec.source_file.path
    doc = fitz.open(input_path)
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    output_dir_rel = f"conversions/output/{base}_images"
    output_dir = _os.path.join(settings.MEDIA_ROOT, output_dir_rel)
    _os.makedirs(output_dir, exist_ok=True)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        pix.save(_os.path.join(output_dir, f"{base}_page_{i+1}.png"))
    doc.close()
    zip_name = f"{base}_images.zip"
    zip_rel = f"conversions/output/{zip_name}"
    zip_path = _os.path.join(settings.MEDIA_ROOT, zip_rel)
    with zipfile.ZipFile(zip_path, "w") as zf:
        for fn in _os.listdir(output_dir):
            zf.write(_os.path.join(output_dir, fn), fn)
    return {"message": f"\u5df2\u751f\u6210 {len(doc)} \u5f20\u56fe\u7247", "filename": zip_name, "path": zip_rel, "download_url": f"{settings.MEDIA_URL}{zip_rel}"}

def _merge_pdfs(recs):
    import fitz
    merged = fitz.open()
    for rec in recs:
        fp = rec.source_file.path if hasattr(rec, "source_file") else rec.file.path
        if fp.lower().endswith(".pdf"):
            doc = fitz.open(fp); merged.insert_pdf(doc); doc.close()
    output_name = f"merged_{_os.urandom(4).hex()}.pdf"
    output_rel = f"conversions/output/{output_name}"
    output_path = _os.path.join(settings.MEDIA_ROOT, output_rel)
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    merged.save(output_path); merged.close()
    return {"message": f"\u5df2\u5408\u5e76 {len(recs)} \u4e2a PDF", "filename": output_name, "path": output_rel, "download_url": f"{settings.MEDIA_URL}{output_rel}"}

def _split_pdf(rec, page_str):
    import fitz; import zipfile
    input_path = rec.source_file.path
    doc = fitz.open(input_path)
    total = len(doc)
    pages = [int(p.strip()) for p in page_str.split(",") if p.strip().isdigit()]
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    output_dir_rel = f"conversions/output/{base}_split"
    output_dir = _os.path.join(settings.MEDIA_ROOT, output_dir_rel)
    _os.makedirs(output_dir, exist_ok=True)
    results = []
    for p in pages:
        if 1 <= p <= total:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
            name = f"{base}_page_{p}.pdf"
            new_doc.save(_os.path.join(output_dir, name)); new_doc.close()
            results.append(name)
    doc.close()
    zip_name = f"{base}_split_pages.zip"
    zip_rel = f"conversions/output/{zip_name}"
    zip_path = _os.path.join(settings.MEDIA_ROOT, zip_rel)
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name in results: zf.write(_os.path.join(output_dir, name), name)
    return {"message": f"\u5df2\u62c6\u5206 {len(results)} \u9875", "filename": zip_name, "path": zip_rel, "download_url": f"{settings.MEDIA_URL}{zip_rel}"}

def _convert_word_to_pdf(rec):
    from docx import Document; import fitz
    input_path = rec.source_file.path
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    doc = Document(input_path)
    pdf_doc = fitz.open()
    page = pdf_doc.new_page()
    page.insert_text(fitz.Point(50, 50), "\n".join([p.text for p in doc.paragraphs]), fontsize=11)
    output_name = f"{base}.pdf"
    output_rel = f"conversions/output/{output_name}"
    output_path = _os.path.join(settings.MEDIA_ROOT, output_rel)
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    pdf_doc.save(output_path); pdf_doc.close()
    return {"message": "Word \u5df2\u8f6c\u6362\u4e3a PDF", "filename": output_name, "path": output_rel, "download_url": f"{settings.MEDIA_URL}{output_rel}"}

def _convert_excel_to_csv(rec):
    import openpyxl; import csv
    input_path = rec.source_file.path
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    wb = openpyxl.load_workbook(input_path, read_only=True)
    ws = wb.active
    output_name = f"{base}.csv"
    output_rel = f"conversions/output/{output_name}"
    output_path = _os.path.join(settings.MEDIA_ROOT, output_rel)
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(list(ws.iter_rows(values_only=True)))
    wb.close()
    return {"message": "Excel \u5df2\u8f6c\u6362\u4e3a CSV", "filename": output_name, "path": output_rel, "download_url": f"{settings.MEDIA_URL}{output_rel}"}

def _convert_excel_to_json(rec):
    import openpyxl; import json
    input_path = rec.source_file.path
    wb = openpyxl.load_workbook(input_path, read_only=True)
    result = {}
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        headers = [str(h) if h else f"col_{i}" for i, h in enumerate(next(ws.iter_rows(values_only=True)))]
        result[sheet_name] = [{headers[i]: (v if v is not None else "") for i, v in enumerate(row)} for row in ws.iter_rows(values_only=True)]
    wb.close()
    base = _os.path.splitext(_os.path.basename(input_path))[0]
    output_name = f"{base}.json"
    output_rel = f"conversions/output/{output_name}"
    output_path = _os.path.join(settings.MEDIA_ROOT, output_rel)
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f: json.dump(result, f, ensure_ascii=False, indent=2)
    return {"message": "Excel \u5df2\u8f6c\u6362\u4e3a JSON", "filename": output_name, "path": output_rel, "download_url": f"{settings.MEDIA_URL}{output_rel}"}

def file_conversion_list(request):
    """获取用户的转换记录"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "\u672a\u767b\u5f55"}, status=401)
    qs = FileConversion.objects.filter(user=request.user).order_by("-created_at")[:20]
    data = []
    for c in qs:
        dl_url = None
        try:
            if c.result_file and _os.path.exists(c.result_file.path):
                dl_url = c.result_file.url
        except: pass
        data.append({"id": c.id, "conv_type": c.conv_type, "conv_type_display": c.get_conv_type_display(), "original_name": c.original_name, "status": c.status, "download_url": dl_url, "error_msg": c.error_msg, "created_at": c.created_at.isoformat()})
    return JsonResponse({"data": data})
