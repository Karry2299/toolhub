import os
import shlex
import shutil
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Pull latest code and run the production update script."

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        update_script = base_dir / "deploy" / "update.sh"

        if not update_script.exists():
            raise CommandError(f"Update script not found: {update_script}")

        if os.name == "nt":
            raise CommandError("Web deploy update only runs on a Linux server. Use run-local.ps1 for local Windows testing.")

        custom_command = os.getenv("TOOLHUB_UPDATE_COMMAND", "").strip()
        if custom_command:
            command = shlex.split(custom_command)
        elif hasattr(os, "geteuid") and os.geteuid() == 0:
            command = ["bash", str(update_script)]
        elif shutil.which("sudo"):
            command = ["sudo", "-n", "bash", str(update_script)]
        else:
            command = ["bash", str(update_script)]

        timeout = int(os.getenv("TOOLHUB_UPDATE_TIMEOUT", "1800"))
        self.stdout.write(self.style.SUCCESS("Starting deploy update..."))
        self.stdout.write("Command: " + " ".join(command))

        try:
            result = subprocess.run(
                command,
                cwd=base_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise CommandError(f"Deploy update timed out after {timeout} seconds") from exc
        except FileNotFoundError as exc:
            raise CommandError("Deploy command not found. Check bash/sudo or TOOLHUB_UPDATE_COMMAND.") from exc

        if result.stdout:
            self.stdout.write(result.stdout)
        if result.stderr:
            self.stderr.write(result.stderr)

        if result.returncode != 0:
            raise CommandError(f"Deploy update failed with exit code {result.returncode}")

        self.stdout.write(self.style.SUCCESS("Deploy update completed."))
