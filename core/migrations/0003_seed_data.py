# Generated data migration - seed demo data
from django.db import migrations
from django.utils import timezone

def seed_data(apps, schema_editor):
    Note = apps.get_model('core', 'Note')
    Todo = apps.get_model('core', 'Todo')
    GeneratedPassword = apps.get_model('core', 'GeneratedPassword')
    SavedQRCode = apps.get_model('core', 'SavedQRCode')
    IPLookupHistory = apps.get_model('core', 'IPLookupHistory')
    ToolUsage = apps.get_model('core', 'ToolUsage')

    # Skip if already seeded
    if Note.objects.exists() or Todo.objects.exists():
        return

    # Sample Notes
    notes = [
        Note(title='欢迎使用个人实用工具', content='这是您的第一条笔记，快来记录些什么吧！'),
        Note(title='使用技巧', content='您可以在笔记中记录任何事情，包括备忘、想法、代码片段等。'),
    ]
    Note.objects.bulk_create(notes)

    # Sample Todos
    todos = [
        Todo(title='体验笔记功能', completed=True),
        Todo(title='生成一个强密码'),
        Todo(title='尝试二维码生成'),
        Todo(title='查询本机 IP'),
    ]
    Todo.objects.bulk_create(todos)

    # Sample password records
    passwords = [
        GeneratedPassword(password='aB3#kL9@mN7&', length=16, has_upper=True, has_lower=True, has_digits=True, has_symbols=True),
        GeneratedPassword(password='MyStr0ng!Pass', length=14, has_upper=True, has_lower=True, has_digits=True, has_symbols=True),
    ]
    GeneratedPassword.objects.bulk_create(passwords)

    # Sample QR codes
    qrcodes = [
        SavedQRCode(content='https://github.com', size=200),
        SavedQRCode(content='https://www.python.org', size=300),
    ]
    SavedQRCode.objects.bulk_create(qrcodes)

    # Sample IP lookups
    lookups = [
        IPLookupHistory(query='8.8.8.8', ip='8.8.8.8', country='United States', region='Virginia', city='Ashburn', org='Google LLC'),
        IPLookupHistory(query='github.com', ip='140.82.121.3', country='United States', region='California', city='San Francisco', org='GitHub, Inc.'),
    ]
    IPLookupHistory.objects.bulk_create(lookups)

    # Sample tool usage
    usages = [
        ToolUsage(tool='notes', action='create', detail='创建了确认笔记'),
        ToolUsage(tool='todo', action='create', detail='添加了待办事项'),
        ToolUsage(tool='password', action='generate', detail='生成了密码长度:16'),
        ToolUsage(tool='qrcode', action='generate', detail='https://github.com'),
        ToolUsage(tool='ip', action='lookup', detail='8.8.8.8'),
    ]
    ToolUsage.objects.bulk_create(usages)


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_generatedpassword_iplookuphistory_savedqrcode_and_more'),
    ]
    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
