"""
数据迁移管理命令
用法: python manage.py data_migrate <action>

Actions:
  - seed      播种示例数据
  - export    导出全部数据为 JSON
  - import    从 JSON 文件导入数据
  - stats     查看数据统计
  - clear     清空所有数据
"""
import json
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

MODELS = ['Note', 'Todo', 'GeneratedPassword', 'SavedQRCode', 'IPLookupHistory', 'ToolUsage']


def get_model(model_name):
    return apps.get_model('core', model_name)


class Command(BaseCommand):
    help = '数据迁移管理工具'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, choices=['seed', 'export', 'import', 'stats', 'clear'])

    def handle(self, *args, **options):
        action = options['action']
        if action == 'seed':
            self._seed()
        elif action == 'export':
            self._export()
        elif action == 'import':
            self._import()
        elif action == 'stats':
            self._stats()
        elif action == 'clear':
            self._clear()

    def _seed(self):
        """播种示例数据"""
        from django.core.management import call_command
        call_command('migrate', 'core', '0003_seed_data')
        self.stdout.write(self.style.SUCCESS('示例数据播种完成'))

    def _export(self):
        """导出数据为 JSON"""
        data = {}
        for name in MODELS:
            model = get_model(name)
            qs = model.objects.all()
            serialized = []
            for obj in qs:
                row = {}
                for field in model._meta.fields:
                    val = getattr(obj, field.name)
                    if hasattr(val, 'isoformat'):
                        val = val.isoformat()
                    row[field.name] = val
                serialized.append(row)
            data[name] = serialized

        path = Path('data_export.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.stdout.write(self.style.SUCCESS(f'数据已导出到 {path}'))

    def _import(self):
        """从 JSON 文件导入数据"""
        path = Path('data_export.json')
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'找不到 {path}'))
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for name in MODELS:
            model = get_model(name)
            rows = data.get(name, [])
            for row in rows:
                row.pop('id', None)
                model.objects.create(**row)
                count += 1
        self.stdout.write(self.style.SUCCESS(f'导入了 {count} 条记录'))

    def _stats(self):
        """数据统计"""
        self.stdout.write('=== 数据库统计 ===')
        total = 0
        for name in MODELS:
            model = get_model(name)
            cnt = model.objects.count()
            total += cnt
            self.stdout.write(f'  {name}: {cnt} 条')
        self.stdout.write(f'  --- 共计: {total} 条记录')

    def _clear(self):
        """清空数据"""
        confirm = input('确定清空所有数据？(yes/no): ')
        if confirm != 'yes':
            self.stdout.write(self.style.WARNING('已取消'))
            return
        for name in reversed(MODELS):
            model = get_model(name)
            model.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('所有数据已清空'))
