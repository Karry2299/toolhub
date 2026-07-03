# ToolHub VPS 部署指南

## 一、购买云服务器

### 推荐配置（最低）
| 配置 | 规格 |
|------|------|
| CPU | 2 核 |
| 内存 | 2 GB |
| 硬盘 | 40 GB |
| 带宽 | 3 Mbps |
| 系统 | Ubuntu 22.04 LTS |

### 国内云厂商推荐
- **阿里云** (aliyun.com) — 轻量应用服务器 2核2G 约 34/月
- **腾讯云** (cloud.tencent.com) — 轻量应用服务器 2核2G 约 38/月
- **华为云** (huaweicloud.com) — HECS 云服务器 2核2G 约 42/月

> 学生优惠：阿里云/腾讯云有学生特惠，9.9/月起

## 二、购买域名

1. **阿里云万网** (wanwang.aliyun.com) — .com/.cn 约 30-50/年
2. **腾讯云 DNSPod** (dnspod.cn) — 域名注册
3. 购买后将域名解析到云服务器的公网 IP

## 三、部署

### SSH 登录服务器
`ash
ssh root@你的服务器IP
`

### 一键部署脚本
`ash
wget -O /tmp/deploy.sh https://raw.githubusercontent.com/Karry2299/toolhub/main/deploy/deploy.sh
nano /tmp/deploy.sh    # 修改 DOMAIN 为你的域名
sudo bash /tmp/deploy.sh
`

## 四、验证

| 地址 | 说明 |
|------|------|
| https://你的域名.com | 网站首页 |
| https://你的域名.com/admin/ | 管理后台 |
| https://你的域名.com/health/ | 健康检查 |

## 五、日常维护

### 更新代码
`ash
cd /var/www/toolhub
git pull
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart toolhub
`

### 查看日志
`ash
sudo journalctl -u toolhub -n 100 -f
`

### 备份数据库
`ash
pg_dump -U toolhub_user toolhub > backup_20260704.sql
`
