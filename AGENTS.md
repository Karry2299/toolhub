# 个人实用功能网站 --- 项目指南

## 项目概述

基于 Django 6.0 + Vue 3 的个人实用功能网站，采用前后端分离架构。

## 技术栈

- **后端**: Python 3.12, Django 6.0.6, SimpleUI (后台美化), SQLite
- **前端**: Vue 3, Vite 8, npm
- **Node.js**: v20.19.3

## 项目结构

```
个人实用功能网站/
|└── AGENTS.md             # 本文件 --- AI 代理指南
|└── config/               # Django 项目配置
|   |└── settings.py       # 主配置（数据库、静态文件、CORS 等）
|   └── urls.py           # 根路由
|└── core/                 # Django 核心应用
|   |└── views.py          # 视图（含 Vue SPA 渲染）
|   |└── urls.py           # 应用路由
|   |└── models.py         # 数据模型
|   └── admin.py          # 后台管理注册
|└── frontend/             # Vue 3 + Vite 前端项目
|   |└── src/              # Vue 源码
|   |└── public/           # 公共静态资源
|   └── vite.config.js    # Vite 配置（含 Django 代理）
|└── static/               # 静态资源目录
|   └── vue/              # Vue 构建产物（Django 自动托管）
|└── manage.py             # Django 管理脚本
└── .venv/                # Python 虚拟环境
```



## 常用命令

### 启动 Django 后端

```powershell
.venv/Scripts/Activate.ps1
python manage.py runserver
```


### 启动 Vue 前端（可选，开发热更新）

```powershell
cd frontend
npm run dev
```

### 构建 Vue 前端

```powershell
cd frontend
npm run build
```

### 数据库操作

```powershell
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
```

## 开发约定

- 新增功能在 core/ 应用中添加
- 修改前端后需运行 npm run build 才能在 Django 中生效
- 开发时同时启动 npm run dev（5173）+ python manage.py runserver（8000）获得热更新体验
- API 端点统一使用 /api/ 前缀
- 模型注册到 core/admin.py 以在后台管理
- .venv/ 和 node_modules/ 不提交到版本控制

## 备忘

- 后台地址: http://127.0.0.1:8000/admin/
- 管理员账号请通过本地 `.env` 或服务器部署脚本单独设置，不写入仓库。

## 关键配置

### Django 设置（config/settings.py）

- **语言**: zh-hans（简体中文）
- **时区**: Asia/Shanghai
- **数据库**: SQLite（db.sqlite3）
- **静态文件 URL**: /static/
- **CORS**: 全来源开放（开发用）
- **已安装应用**: simpleui, corsheaders, django.contrib.admin, core

### 路由结构

- /admin/ -> Django 管理后台（SimpleUI）
- / -> Vue SPA（core.views.index）

### Vue 构建配置（frontend/vite.config.js）

- base: /static/vue/
- 构建输出到: ../static/vue/
- 开发代理 /api/* -> http://127.0.0.1:8000
- 开发端口: 5173

## 数据库设计

### 数据模型一览
- [Note] - 记事本（title, content, created_at, updated_at）
- [Todo] - 待办事项（title, completed, created_at）
- [GeneratedPassword] - 生成的密码记录（password, length, 字符类型选项, created_at）
- [SavedQRCode] - 保存的二维码记录（content, size, created_at）
- [IPLookupHistory] - IP 查询历史（query, ip, country, region, city, org, created_at）
- [ToolUsage] - 工具使用日志（tool, action, detail, created_at）

### API 端点
- /api/notes/ - Note CRUD
- /api/todos/ - Todo CRUD
- /api/passwords/ - 密码记录 CRUD
- /api/qrcodes/ - 二维码记录 CRUD
- /api/ip-lookups/ - IP 查询历史 CRUD
- /api/tool-usage/ - 工具使用日志
- /api/qrcode/?text=xxx&size=200 - 生成二维码图片
- /api/ip-lookup/?q=8.8.8.8 - IP 归属地查询
- /api/password/save/ - 保存生成的密码
