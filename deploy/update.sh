#!/bin/bash
# ===== ToolHub 一键更新脚本 =====
# 在服务器上执行: sudo bash deploy/update.sh
set -e

echo "==========================================="
echo "  🔄 ToolHub 一键更新"
echo "==========================================="

cd /var/www/toolhub

echo ""
echo "[1/6] 从 GitHub 拉取最新代码..."
git pull

echo ""
echo "[2/6] 安装 Python 依赖..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[3/6] 构建前端..."
cd frontend
npm install
npm run build
cd ..

echo ""
echo "[4/6] 执行数据库迁移..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

echo ""
echo "[5/6] 设置目录权限..."
chown -R www-data:www-data /var/www/toolhub
chmod -R 755 /var/www/toolhub/media

echo ""
echo "[6/6] 重启服务..."
systemctl restart toolhub

echo ""
echo "==========================================="
echo "  ✅ 更新完成！"
echo "==========================================="
