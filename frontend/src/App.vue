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
            <router-link to="/notes" class="nav-link">&#31508;&#35760;</router-link>
            <router-link to="/todo" class="nav-link">&#24453;&#21150;</router-link>
            <router-link to="/password" class="nav-link">&#23494;&#30721;</router-link>
            <router-link to="/qrcode" class="nav-link">&#20108;&#32500;&#30721;</router-link>
            <router-link to="/ip-lookup" class="nav-link">IP&#26597;&#35810;</router-link>
            <router-link to="/files" class="nav-link">&#25991;&#20214;</router-link>
          </nav>
          <div class="header-right">
            <span class="user-name">{{ auth.user?.username }}</span>
            <button @click="handleLogout" class="btn btn-ghost logout-btn">&#36864;&#20986;</button>
          </div>
        </div>
      </header>
      <main class="app-main">
        <router-view />
      </main>
    </template>
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup>
import { auth, authHeaders } from "./auth.js"
import { useRouter } from "vue-router"
const router = useRouter()
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
</style>
