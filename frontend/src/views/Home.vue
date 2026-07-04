<template>
  <div class="home">
    <div class="home-header">
      <h1 class="home-title">ToolHub</h1>
      <p class="home-subtitle">一站式实用工具集合</p>
    </div>
    <div class="tool-grid">
      <router-link to="/notes" class="tool-card" style="--accent: #3b82f6">
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">📝</div>
          <h3 class="card-title">在线笔记</h3>
          <p class="card-desc">随时随地记录想法与备忘</p>
        </div>
      </router-link>
      <router-link to="/todo" class="tool-card" style="--accent: #22c55e">
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">✅</div>
          <h3 class="card-title">待办事项</h3>
          <p class="card-desc">管理日常任务清单</p>
        </div>
      </router-link>
      <router-link to="/password" class="tool-card" style="--accent: #f59e0b">
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">🔑</div>
          <h3 class="card-title">密码生成器</h3>
          <p class="card-desc">创建强大的密码</p>
        </div>
      </router-link>
      <router-link to="/qrcode" class="tool-card" style="--accent: #8b5cf6">
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">📱</div>
          <h3 class="card-title">二维码生成</h3>
          <p class="card-desc">链接与文字转为二维码</p>
        </div>
      </router-link>
      <router-link to="/ip-lookup" class="tool-card" style="--accent: #06b6d4">
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">🌐</div>
          <h3 class="card-title">IP/域名查询</h3>
          <p class="card-desc">获取 IP 归属地信息</p>
        </div>
      </router-link>
      <router-link to="/files" class="tool-card" style="--accent: #ec4899">
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">📁</div>
          <h3 class="card-title">文件管理器</h3>
          <p class="card-desc">上传、收藏、分享文件</p>
        </div>
      </router-link>
    </div>
  </div>
  <div v-if="isAdmin" class="admin-section">
    <div class="section-header" style="display:flex;justify-content:space-between;align-items:center;margin-top:40px;margin-bottom:16px;">
      <h2 style="font-size:1.2em;font-weight:600;color:var(--text-primary);">🔧 系统管理</h2>
    </div>
    <button @click="startDeploy" :disabled="deploying" class="deploy-btn" style="display:inline-flex;align-items:center;gap:8px;padding:10px 24px;border:none;border-radius:var(--radius-md);cursor:pointer;font-size:0.9em;background:linear-gradient(135deg,#409EFF,#337ecc);color:#fff;transition:all 0.3s;">
      <span>{{ deploying ? "⏳ 更新中..." : "🚀 一键部署更新" }}</span>
    </button>
    <div v-if="deployResult" :style="{marginTop:'12px',padding:'10px 14px',borderRadius:'var(--radius-md)',fontSize:'0.85em',background:deployResult.success ? '#f0f9f0' : '#fef0f0',color:deployResult.success ? '#67c23a' : '#f56c6c',border:'1px solid ' + (deployResult.success ? '#e1f3d8' : '#fde2e2')}">
      {{ deployResult.message }}
    </div>
    <pre v-if="deployOutput" style="margin-top:10px;padding:12px;background:#1e1e1e;color:#d4d4d4;border-radius:6px;max-height:300px;overflow-y:auto;font-size:12px;line-height:1.5;white-space:pre-wrap;">{{ deployOutput }}</pre>
  </div>
</template>
<script setup>
import { ref } from "vue"
import { auth, authHeaders } from "../auth.js"

const isAdmin = auth.user?.is_superuser || false
const deploying = ref(false)
const deployResult = ref(null)
const deployOutput = ref("")

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
</script>
<style scoped>
.home-header { text-align: center; padding: 40px 0 48px; }
.home-title { font-size: 2.5em; font-weight: 700; color: var(--text-primary); letter-spacing: -0.03em; margin-bottom: 8px; }
.home-subtitle { font-size: 1em; color: var(--text-secondary); font-weight: 400; }
.tool-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; padding-bottom: 40px; }
.tool-card { display: block; background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border-default); text-decoration: none; color: inherit; overflow: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; }
.tool-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); border-color: transparent; }
.card-accent { height: 3px; background: var(--accent); width: 100%; }
.card-body { padding: 28px 24px 24px; }
.card-icon { font-size: 2em; margin-bottom: 14px; }
.card-title { font-size: 1.05em; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }
.card-desc { font-size: 0.82em; color: var(--text-secondary); line-height: 1.5; }
</style>