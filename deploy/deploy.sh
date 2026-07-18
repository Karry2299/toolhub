#!/bin/bash
set -e

# ===== ToolHub 服务器一键部署脚本 =====
# 适用系统: Ubuntu 22.04 / Debian 12
# 使用方法: sudo bash deploy.sh

echo "==========================================="
echo "  ToolHub 一键部署脚本"
echo "==========================================="

# 配置区域 —— 请修改为你的实际信息
DOMAIN="yourdomain.com"              # 你的域名
GIT_REPO="https://github.com/Karry2299/toolhub.git"
DB_PASSWORD=$(openssl rand -base64 16)  # 自动生成数据库密码
ADMIN_USER="admin"
ADMIN_PASSWORD=$(openssl rand -base64 18)  # 首次登录后请修改

# ============================================

# 1. 系统更新 & 安装依赖
echo "[1/8] 更新系统并安装依赖..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv python3-dev
apt install -y nginx certbot postgresql postgresql-contrib
apt install -y git nodejs npm redis-server
apt install -y python3-certbot-nginx

# 2. 配置 PostgreSQL
echo "[2/8] 配置 PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE USER toolhub_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE toolhub OWNER toolhub_user;
GRANT ALL PRIVILEGES ON DATABASE toolhub TO toolhub_user;
EOF

# 3. 克隆代码
echo "[3/8] 部署代码..."
mkdir -p /var/www/toolhub
cd /var/www/toolhub
git clone $GIT_REPO .

# 4. 创建虚拟环境 & 安装 Python 依赖
echo "[4/8] 安装 Python 依赖..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# 5. 构建前端
echo "[5/8] 构建前端..."
cd frontend
npm install
npm run build
cd ..

# 6. 配置环境变量
echo "[6/8] 配置环境..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
cat > .env <<EOF
DJANGO_SECRET_KEY=$SECRET_KEY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
DJANGO_CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
DATABASE_URL=postgres://toolhub_user:$DB_PASSWORD@127.0.0.1:5432/toolhub
EOF

# 7. 数据库迁移 & 静态文件
echo "[7/8] 执行数据库迁移..."
source .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

# 创建管理员
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USER', 'admin@$DOMAIN', '$ADMIN_PASSWORD') if not User.objects.filter(username='$ADMIN_USER').exists() else None" | python manage.py shell

# 设置目录权限
chown -R www-data:www-data /var/www/toolhub
chmod -R 755 /var/www/toolhub/media

# 8. 配置 Nginx & 启动服务
echo "[8/8] 配置 Nginx 并启动..."
# 复制 Nginx 配置
ln -sf /var/www/toolhub/deploy/toolhub.nginx.conf /etc/nginx/sites-available/toolhub.conf
ln -sf /etc/nginx/sites-available/toolhub.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 配置 SSL 证书
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m "admin@$DOMAIN"

# 配置 Systemd 服务
ln -sf /var/www/toolhub/deploy/toolhub.service /etc/systemd/system/toolhub.service
systemctl daemon-reload
systemctl enable toolhub
systemctl start toolhub

echo ""
echo "==========================================="
echo "  ✅ 部署完成！"
echo "==========================================="
echo "  网站: https://$DOMAIN"
echo "  后台: https://$DOMAIN/admin/"
echo "  管理员: $ADMIN_USER / $ADMIN_PASSWORD"
echo "  数据库密码: $DB_PASSWORD"
echo ""
echo "  ⚠️  请立即修改管理员密码！"
echo "==========================================="
