<template>
  <div class="home">
    <!-- Hero Section -->
    <div class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-icon">
          <svg viewBox="0 0 40 40" width="48" height="48" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="36" height="36" rx="10" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
            <g fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 15 L16 11 Q18 9 20 11 L18 13 L20 15 Q22 17 20 19 L16 15 L12 19 Q10 17 12 15Z"/>
              <line x1="16" y1="15" x2="26" y2="25"/>
              <line x1="22" y1="22" x2="28" y2="28"/>
            </g>
          </svg>
        </div>
        <h1 class="hero-title">ToolHub</h1>
        <p class="hero-subtitle">一站式实用工具集合</p>
      </div>
    </div>

    <!-- Server Status Dashboard -->
    <div v-if="isLoggedIn" class="dashboard">
      <div class="dashboard-header">
        <h2 class="dashboard-title">服务器状态</h2>
        <button @click="refreshStatus" class="btn-ghost-sm" :disabled="serverLoading">{{ serverLoading ? '刷新中...' : '🔄 刷新' }}</button>
      </div>
      <div class="metric-grid">
        <div class="metric-card">
          <div class="metric-icon" style="background:linear-gradient(135deg,#3b82f6,#1d4ed8);">💾</div>
          <div class="metric-body">
            <div class="metric-label">磁盘使用</div>
            <div class="metric-value">{{ serverStatus.disk.used || "0" }} <small>GB</small></div>
            <div class="metric-bar"><div class="metric-fill" :style="{width:(serverStatus.disk.percent||0)+'%',background:(serverStatus.disk.percent||0)>80?'#ef4444':'#3b82f6'}"></div></div>
            <div class="metric-detail">总计 {{ serverStatus.disk.total || "-" }} GB · 已用 {{ (serverStatus.disk.percent || 0) }}%</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon" style="background:linear-gradient(135deg,#22c55e,#16a34a);">💡</div>
          <div class="metric-body">
            <div class="metric-label">内存使用</div>
            <div class="metric-value">{{ (serverStatus.memory.percent || 0) }}<small>%</small></div>
            <div class="metric-bar"><div class="metric-fill" :style="{width:(serverStatus.memory.percent||0)+'%',background:(serverStatus.memory.percent||0)>80?'#ef4444':'#22c55e'}"></div></div>
            <div class="metric-detail">已用 {{ formatBytes(serverStatus.memory.used || 0) }}</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon" style="background:linear-gradient(135deg,#f59e0b,#d97706);">⚙️</div>
          <div class="metric-body">
            <div class="metric-label">CPU 使用</div>
            <div class="metric-value">{{ (serverStatus.cpu.percent || 0) }}<small>%</small></div>
            <div class="metric-bar"><div class="metric-fill" :style="{width:(serverStatus.cpu.percent||0)+'%',background:(serverStatus.cpu.percent||0)>80?'#ef4444':'#f59e0b'}"></div></div>
            <div class="metric-detail">实时负载</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Admin Deploy -->
    <div v-if="isAdmin" class="admin-section">
      <div class="dashboard-header">
        <h2 class="dashboard-title">🚀 系统部署</h2>
      </div>
      <div class="admin-card">
        <div class="admin-info">
          <div class="admin-info-title">一键部署更新</div>
          <div class="admin-info-desc">从 GitHub 拉取最新代码，自动安装依赖、构建前端、迁移数据库、重启服务</div>
        </div>
        <button @click="startDeploy" :disabled="deploying" class="admin-btn">
          {{ deploying ? '⏳ 更新中...' : '🚀 开始更新' }}
        </button>
      </div>
      <div v-if="deployResult" class="deploy-result" :class="{success:deployResult.success,error:!deployResult.success}">
        {{ deployResult.message }}
      </div>
      <pre v-if="deployOutput" class="deploy-log">{{ deployOutput }}</pre>
    </div>

    <!-- Tools Grid -->
    <div class="tools-section">
      <h2 class="section-label">实用工具</h2>
      <div class="tool-grid">
        <router-link to="/notes" class="tool-card" style="--accent: #3b82f6">
          <div class="tc-icon" style="background:rgba(59,130,246,0.1);color:#3b82f6;">📓</div>
          <h3 class="tc-title">在线笔记</h3>
          <p class="tc-desc">随时随地记录想法与备忘</p>
        </router-link>
        <router-link to="/todo" class="tool-card" style="--accent: #22c55e">
          <div class="tc-icon" style="background:rgba(34,197,94,0.1);color:#22c55e;">✅</div>
          <h3 class="tc-title">待办事项</h3>
          <p class="tc-desc">管理日常任务清单</p>
        </router-link>
        <router-link to="/password" class="tool-card" style="--accent: #f59e0b">
          <div class="tc-icon" style="background:rgba(245,158,11,0.1);color:#f59e0b;">🔒</div>
          <h3 class="tc-title">密码生成器</h3>
          <p class="tc-desc">创建安全的随机密码</p>
        </router-link>
        <router-link to="/qrcode" class="tool-card" style="--accent: #8b5cf6">
          <div class="tc-icon" style="background:rgba(139,92,246,0.1);color:#8b5cf6;">📫</div>
          <h3 class="tc-title">二维码生成</h3>
          <p class="tc-desc">链接与文本转二维码</p>
        </router-link>
        <router-link to="/ip-lookup" class="tool-card" style="--accent: #06b6d4">
          <div class="tc-icon" style="background:rgba(6,182,212,0.1);color:#06b6d4;">🌊</div>
          <h3 class="tc-title">IP 查询</h3>
          <p class="tc-desc">查询 IP 归属地信息</p>
        </router-link>
        <router-link to="/files" class="tool-card" style="--accent: #ec4899">
          <div class="tc-icon" style="background:rgba(236,72,153,0.1);color:#ec4899;">📁</div>
          <h3 class="tc-title">文件管理</h3>
          <p class="tc-desc">上传、收藏、分享文件</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { auth, authHeaders } from "../auth.js"

const isLoggedIn = auth.isLoggedIn
const isAdmin = auth.user?.is_superuser || false
const serverStatus = ref({ disk: { total:0, used:0, percent:0 }, memory: { total:0, used:0, percent:0 }, cpu: { percent:0 } })
const serverLoading = ref(false)
const deploying = ref(false)
const deployResult = ref(null)
const deployOutput = ref("")

function formatBytes(bytes) {
  if (!bytes) return "0 B"
  const gb = bytes / (1024*1024*1024)
  if (gb >= 1) return gb.toFixed(1) + " GB"
  const mb = bytes / (1024*1024)
  if (mb >= 1) return mb.toFixed(0) + " MB"
  return (bytes / 1024).toFixed(0) + " KB"
}

async function fetchServerStatus() {
  if (!isLoggedIn) return
  serverLoading.value = true
  try {
    const r = await fetch("/api/server/status/", { headers: authHeaders() })
    if (r.ok) {
      const data = await r.json()
      if (data.disk) serverStatus.value = data
    }
  } catch (e) {} finally { serverLoading.value = false }
}

async function refreshStatus() { await fetchServerStatus() }

async function startDeploy() {
  deploying.value = true
  deployResult.value = null
  deployOutput.value = ""
  try {
    const r = await fetch("/api/deploy/update/", { method: "POST", headers: authHeaders() })
    const data = await r.json()
    deployResult.value = { success: data.success, message: data.message || "更新完成" }
    deployOutput.value = data.output || ""
  } catch (e) {
    deployResult.value = { success: false, message: "请求失败: " + e.message }
  } finally {
    deploying.value = false
  }
}

onMounted(() => { fetchServerStatus() })</script>

<style scoped>
.home { max-width: var(--max-width); margin: 0 auto; padding: 0 24px 40px; }

/* Hero */
.hero { position: relative; text-align: center; padding: 48px 0 40px; margin-bottom: 8px; }
.hero-bg { position:absolute; inset:0; background: radial-gradient(ellipse at 50% 0%, rgba(245,158,11,0.06) 0%, transparent 60%); pointer-events:none; }
.hero-content { position:relative; z-index:1; }
.hero-icon { margin-bottom:16px; display:inline-block; }
.hero-title { font-size:2.4em; font-weight:800; color:var(--text-primary); letter-spacing:-0.04em; margin-bottom:6px; line-height:1.2; }
.hero-subtitle { font-size:1em; color:var(--text-secondary); font-weight:400; }

/* Dashboard */
.dashboard { margin-bottom:40px; }
.dashboard-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.dashboard-title { font-size:1.1em; font-weight:600; color:var(--text-primary); letter-spacing:-0.01em; }
.btn-ghost-sm { padding:6px 14px; border:1px solid var(--border-default); border-radius:var(--radius-sm); background:transparent; color:var(--text-secondary); font-size:0.82em; cursor:pointer; transition:all 0.2s; }
.btn-ghost-sm:hover { border-color:var(--text-tertiary); color:var(--text-primary); }
.btn-ghost-sm:disabled { opacity:0.5; cursor:default; }
.metric-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; }
.metric-card { background:var(--bg-card); border:1px solid var(--border-default); border-radius:var(--radius-lg); padding:20px; display:flex; gap:16px; transition:all 0.2s; }
.metric-card:hover { box-shadow:var(--shadow-lg); border-color:transparent; transform:translateY(-2px); }
.metric-icon { width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.3em; flex-shrink:0; }
.metric-body { flex:1; min-width:0; }
.metric-label { font-size:0.82em; color:var(--text-secondary); font-weight:500; margin-bottom:2px; }
.metric-value { font-size:1.8em; font-weight:700; color:var(--text-primary); letter-spacing:-0.03em; line-height:1.2; margin-bottom:8px; }
.metric-value small { font-size:0.45em; font-weight:500; color:var(--text-secondary); }
.metric-bar { height:4px; background:#e5e7eb; border-radius:2px; margin-bottom:6px; }
.metric-fill { height:100%; border-radius:2px; transition:width 0.6s ease; }
.metric-detail { font-size:0.78em; color:var(--text-tertiary); }

/* Tools */
.tools-section { }
.section-label { font-size:1.1em; font-weight:600; color:var(--text-primary); margin-bottom:16px; letter-spacing:-0.01em; }
.tool-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:16px; }
.tool-card { display:block; background:var(--bg-card); border:1px solid var(--border-default); border-radius:var(--radius-md); padding:28px 24px; text-decoration:none; transition:all 0.25s cubic-bezier(0.4,0,0.2,1); }
.tool-card:hover { transform:translateY(-3px); box-shadow:var(--shadow-lg); border-color:transparent; }
.tc-icon { width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.4em; margin-bottom:16px; }
.tc-title { font-size:1em; font-weight:600; color:var(--text-primary); margin-bottom:6px; }
.tc-desc { font-size:0.82em; color:var(--text-secondary); line-height:1.5; }

/* Admin */
.admin-section { margin-top:24px; margin-bottom:40px; }
.admin-card { background:var(--bg-card); border:1px solid var(--border-default); border-radius:var(--radius-lg); padding:20px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; }
.admin-card:hover { box-shadow:var(--shadow-lg); border-color:transparent; }
.admin-info { flex:1; }
.admin-info-title { font-size:0.95em; font-weight:600; color:var(--text-primary); margin-bottom:4px; }
.admin-info-desc { font-size:0.82em; color:var(--text-secondary); line-height:1.5; }
.admin-btn { padding:10px 28px; border:none; border-radius:var(--radius-sm); cursor:pointer; font-size:0.88em; font-weight:500; background:linear-gradient(135deg,#409EFF,#337ecc); color:#fff; white-space:nowrap; }
.admin-btn:hover { box-shadow:var(--shadow-md); transform:translateY(-1px); }
.admin-btn:disabled { opacity:0.6; cursor:default; transform:none; }
.deploy-result { margin-top:10px; padding:10px 14px; border-radius:var(--radius-sm); font-size:0.85em; }
.deploy-result.success { background:#f0f9f0; color:#67c23a; border:1px solid #e1f3d8; }
.deploy-result.error { background:#fef0f0; color:#f56c6c; border:1px solid #fde2e2; }
.deploy-log { margin-top:10px; padding:12px; background:#1e1e1e; color:#d4d4d4; border-radius:var(--radius-sm); max-height:280px; overflow-y:auto; font-size:12px; line-height:1.5; white-space:pre-wrap; }

</style>