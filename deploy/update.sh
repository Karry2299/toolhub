#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="${TOOLHUB_SERVICE_NAME:-toolhub}"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/snap/bin:${PATH}"

echo "==========================================="
echo "  ToolHub deploy update"
echo "==========================================="
echo "App directory: ${APP_DIR}"

cd "${APP_DIR}"

echo ""
echo "[1/6] Pull latest code..."
git config --global --add safe.directory "${APP_DIR}" >/dev/null 2>&1 || true
git config --global http.version HTTP/1.1 >/dev/null 2>&1 || true
git config --global http.postBuffer 524288000 >/dev/null 2>&1 || true

pull_ok=0
for attempt in 1 2 3; do
  echo "Git pull attempt ${attempt}/3..."
  if git pull --ff-only; then
    pull_ok=1
    break
  fi
  echo "Git pull failed, retrying in 5 seconds..."
  sleep 5
done

if [ "${pull_ok}" -ne 1 ]; then
  echo "Git pull failed after 3 attempts."
  exit 1
fi

echo ""
echo "[2/6] Install Python dependencies..."
if [ ! -f ".venv/bin/activate" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ""
echo "[3/6] Build Vue frontend..."
if ! command -v npm >/dev/null 2>&1; then
  echo "npm command not found. Install Node.js 20+ and make sure npm is available in /usr/bin or /usr/local/bin."
  exit 127
fi
echo "Node version: $(node -v 2>/dev/null || echo unavailable)"
echo "npm version: $(npm -v)"
cd frontend
if [ -f "package-lock.json" ]; then
  npm ci
else
  npm install
fi
npm run build
cd ..

echo ""
echo "[4/6] Run database migrations and collect static files..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

echo ""
echo "[5/6] Fix media permissions when possible..."
if [ "$(id -u)" -eq 0 ]; then
  if id www-data >/dev/null 2>&1; then
    chown -R www-data:www-data "${APP_DIR}"
  fi
  chmod -R 755 "${APP_DIR}/media" || true
else
  echo "Not running as root; skipped chown. Ensure the web service can read/write media."
fi

echo ""
echo "[6/6] Restart service..."
if command -v systemctl >/dev/null 2>&1; then
  systemctl restart "${SERVICE_NAME}"
else
  echo "systemctl not found; skipped service restart."
fi

echo ""
echo "==========================================="
echo "  Deploy update completed"
echo "==========================================="
