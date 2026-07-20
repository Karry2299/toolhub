<template>
  <div id="app">
    <template v-if="auth.isLoggedIn">
      <header class="app-header">
        <div class="header-inner">
          <router-link to="/" class="logo">
            <span class="logo-icon">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="28" height="28" style="display:block">
    <defs>
      <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#f59e0b"/>
        <stop offset="100%" stop-color="#d97706"/>
      </linearGradient>
    </defs>
    <rect x="2" y="2" width="32" height="32" rx="8" fill="#0f172a" stroke="url(#lg)" stroke-width="1.5"/>
    <g fill="none" stroke="url(#lg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M11 14 L15 10 Q17 8 19 10 L17 12 L19 14 Q21 16 19 18 L15 14 L11 18 Q9 16 11 14Z"/>
      <line x1="15" y1="14" x2="24" y2="23"/>
      <line x1="21" y1="21" x2="26" y2="26"/>
    </g>
  </svg>
</span>
            <span class="logo-text">ToolHub</span>
          </router-link>
          <nav class="app-nav">
            <router-link to="/dashboard" class="nav-link">仪表盘</router-link>
            <router-link to="/notes" class="nav-link">笔记</router-link>
            <router-link to="/todo" class="nav-link">待办</router-link>
            <router-link to="/productivity" class="nav-link">效率</router-link>
            <router-link to="/utility-tools" class="nav-link">工具箱</router-link>
            <router-link to="/image-organizer" class="nav-link">图片</router-link>
            <router-link to="/password" class="nav-link">密码</router-link>
            <router-link to="/files" class="nav-link">文件</router-link>
          </nav>
          <div class="header-right">
            <div class="theme-switcher" title="切换网站风格">
              <button
                v-for="item in themes"
                :key="item.key"
                class="theme-dot"
                :class="{ active: theme === item.key }"
                :style="{ '--theme-color': item.color }"
                :title="item.name"
                @click="setTheme(item.key)"
              >
                <span class="sr-only">{{ item.name }}</span>
              </button>
            </div>
            <span class="user-name">{{ auth.user?.username }}</span>
            <button @click="handleLogout" class="btn btn-ghost logout-btn">退出</button>
          </div>
        </div>
      </header>
      <main class="app-main">
        <router-view />
      </main>
    </template>
    <template v-else>
      <div class="guest-theme-switcher" title="切换网站风格">
        <button
          v-for="item in themes"
          :key="item.key"
          class="theme-dot"
          :class="{ active: theme === item.key }"
          :style="{ '--theme-color': item.color }"
          :title="item.name"
          @click="setTheme(item.key)"
        >
          <span class="sr-only">{{ item.name }}</span>
        </button>
      </div>
      <router-view />
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { auth, authHeaders } from "./auth.js"
import { useRouter } from "vue-router"
const router = useRouter()

const themes = [
  { key: "classic", name: "经典", color: "#f59e0b" },
  { key: "ocean", name: "海蓝", color: "#0ea5e9" },
  { key: "forest", name: "森林", color: "#16a34a" },
  { key: "sunset", name: "暮色", color: "#e11d48" },
  { key: "midnight", name: "暗夜", color: "#8b5cf6" },
]

const savedTheme = localStorage.getItem("toolhub-theme")
const theme = ref(themes.some((item) => item.key === savedTheme) ? savedTheme : "classic")

function setTheme(nextTheme) {
  theme.value = nextTheme
  document.documentElement.dataset.theme = nextTheme
  localStorage.setItem("toolhub-theme", nextTheme)
}

onMounted(() => setTheme(theme.value))

async function handleLogout() {
  try { await fetch("/api/auth/logout/", { method: "POST", headers: authHeaders() }) } catch (e) {}
  auth.logout()
  router.push("/login")
}
</script>

<style>
.app-header {
  background: var(--bg-header);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.header-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 24px;
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}
.logo-icon { font-size: 1.3em; color: var(--bg-accent); }
.logo-text { font-size: 1.2em; font-weight: 700; color: var(--text-inverse); letter-spacing: -0.02em; }
.app-nav { display: flex; gap: 2px; }
.nav-link {
  padding: 8px 16px; text-decoration: none; color: rgba(255,255,255,0.7);
  border-radius: var(--radius-sm); font-size: 0.88em; font-weight: 500;
  transition: all 0.2s ease; letter-spacing: 0.01em;
}
.nav-link:hover { color: var(--text-inverse); background: rgba(255,255,255,0.08); }
.nav-link.router-link-active { color: var(--text-inverse); background: rgba(245,158,11,0.15); }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-name { color: rgba(255,255,255,0.8); font-size: 0.85em; font-weight: 500; }
.theme-switcher,
.guest-theme-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px;
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
}
.guest-theme-switcher {
  position: fixed;
  top: 18px;
  right: 18px;
  z-index: 20;
  border-color: var(--border-default);
  background: color-mix(in srgb, var(--bg-card) 86%, transparent);
  box-shadow: var(--shadow-md);
}
.theme-dot {
  width: 22px;
  height: 22px;
  border: 2px solid transparent;
  border-radius: 50%;
  background: var(--theme-color);
  cursor: pointer;
  box-shadow: inset 0 0 0 2px rgba(255,255,255,0.5);
  transition: transform 0.16s ease, border-color 0.16s ease;
}
.theme-dot:hover { transform: translateY(-1px); }
.theme-dot.active {
  border-color: var(--text-inverse);
  transform: scale(1.08);
}
.guest-theme-switcher .theme-dot.active { border-color: var(--text-primary); }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.logout-btn {
  color: rgba(255,255,255,0.6) !important;
  border-color: rgba(255,255,255,0.15) !important;
  padding: 6px 14px; font-size: 0.82em; cursor: pointer;
}
.logout-btn:hover { color: var(--text-inverse) !important; border-color: rgba(255,255,255,0.3) !important; }
.app-main {
  max-width: var(--max-width); margin: 0 auto; padding: 32px 24px;
  min-height: calc(100vh - var(--header-height));
}

@media (max-width: 920px) {
  .app-header { position: sticky; }
  .header-inner {
    height: auto;
    min-height: var(--header-height);
    padding: 10px 14px 8px;
    flex-wrap: wrap;
    gap: 10px;
  }
  .logo { flex: 1; min-width: 120px; }
  .app-nav {
    order: 3;
    width: 100%;
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 8px 0 2px;
    scrollbar-width: none;
  }
  .app-nav::-webkit-scrollbar { display: none; }
  .nav-link {
    flex: 0 0 auto;
    padding: 8px 12px;
    font-size: 0.86em;
    background: rgba(255,255,255,0.05);
  }
  .header-right {
    gap: 8px;
    flex: 0 0 auto;
  }
  .user-name { display: none; }
  .logout-btn {
    padding: 6px 10px;
    font-size: 0.8em;
  }
  .theme-switcher { gap: 4px; }
  .theme-dot { width: 20px; height: 20px; }
  .app-main {
    padding: 18px 12px 28px;
    min-height: calc(100vh - 112px);
  }
}

@media (max-width: 420px) {
  .logo-text { font-size: 1.05em; }
  .theme-dot { width: 18px; height: 18px; }
  .theme-switcher { padding: 3px; }
  .logout-btn { padding: 6px 8px; }
  .guest-theme-switcher {
    top: 10px;
    right: 10px;
  }
}
</style>
