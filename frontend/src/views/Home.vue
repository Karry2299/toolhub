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
</template>
<script setup>
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