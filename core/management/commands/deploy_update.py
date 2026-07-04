import subprocess
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "从 GitHub 拉取最新代码并部署更新"

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        update_script = base_dir / "deploy" / "update.sh"

        if not update_script.exists():
            self.stderr.write(self.style.ERROR(f"更新脚本不存在: {update_script}"))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("🔄 开始一键更新...\n"))

        try:
            result = subprocess.run(
                ["sudo", "bash", str(update_script)],
                cwd=base_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            self.stdout.write(result.stdout)

            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS("✅ 更新完成！"))
            else:
                self.stderr.write(self.style.ERROR(f"❌ 更新失败 (code {result.returncode}):"))
                self.stderr.write(result.stderr)
                sys.exit(1)

        except subprocess.TimeoutExpired:
            self.stderr.write(self.style.ERROR("❌ 更新超时（超过 5 分钟）"))
            sys.exit(1)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ 未找到 sudo 命令"))
            sys.exit(1)
