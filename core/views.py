import io
import json
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets
from .models import Note, Todo, GeneratedPassword, SavedQRCode, IPLookupHistory, ToolUsage
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
        serializer.save(user=self.request.user)

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
        return JsonResponse({'token': token.key, 'username': user.username, 'user_id': user.id})
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
            return JsonResponse({'token': token.key, 'username': user.username, 'user_id': user.id})
        return JsonResponse({'error': '\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
def me_api(request):
    token_key = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
    try:
        token = Token.objects.get(key=token_key)
        return JsonResponse({'username': token.user.username, 'user_id': token.user.id})
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
    file_obj = get_object_or_404(UploadedFile, share_token=token)
    serializer = UploadedFileSerializer(file_obj)
    data = serializer.data
    data['share_url'] = request.build_absolute_uri(f"/api/files/shared/{token}/")
    data['download_url'] = request.build_absolute_uri(f"/api/files/{file_obj.pk}/download/")
    return JsonResponse(data)
