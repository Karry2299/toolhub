<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <div class="auth-logo-wrap">
          <svg viewBox="0 0 40 40" width="40" height="40" style="display:block;margin:0 auto 8px" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="36" height="36" rx="10" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
            <g fill="none" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 16 L17 11 Q19 9 21 11 L19 13 L21 16 Q23 18 21 20 L17 16 L12 20 Q10 18 12 16Z"/>
              <line x1="17" y1="16" x2="27" y2="26"/>
              <line x1="24" y1="24" x2="29" y2="29"/>
            </g>
          </svg>
          <h1 class="auth-logo">ToolHub</h1>
        </div>
        <p class="auth-desc">创建新账户</p>
      </div>
      <form @submit.prevent="register" class="auth-form">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" class="input" placeholder="输入用户名" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" class="input" placeholder="输入密码，至少 6 位" required minlength="6" />
        </div>
        <div class="field">
          <label>确认密码</label>
          <input v-model="confirmPwd" type="password" class="input" placeholder="再次输入密码" required />
        </div>
        <p v-if="error" class="auth-error">{{ error }}</p>
        <button type="submit" class="btn btn-accent auth-btn" :disabled="loading">
          {{ loading ? "注册中..." : "注册" }}
        </button>
      </form>
      <p class="auth-footer">已有账号？ <router-link to="/login" class="auth-link">立即登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { auth } from "../auth.js"

const router = useRouter()
const username = ref("")
const password = ref("")
const confirmPwd = ref("")
const error = ref("")
const loading = ref(false)

async function register() {
  error.value = ""
  if (password.value !== confirmPwd.value) {
    error.value = "两次密码不一致"
    return
  }
  loading.value = true
  try {
    const r = await fetch("/api/auth/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    const data = await r.json()
    if (r.ok) {
      auth.login(data.token, { username: data.username, id: data.user_id, is_superuser: data.is_superuser })
      router.push("/")
    } else {
      error.value = data.error || "注册失败"
    }
  } catch (e) {
    error.value = "网络错误"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 200px); }
.auth-card { padding: 40px; max-width: 380px; width: 100%; }
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-logo-wrap { text-align: center; margin-bottom: 8px; }
.auth-logo { font-size: 1.6em; font-weight: 700; color: var(--text-primary); }
.auth-desc { font-size: 0.9em; color: var(--text-secondary); margin-top: 6px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 0.85em; font-weight: 500; color: var(--text-secondary); }
.auth-btn { width: 100%; padding: 12px; justify-content: center; font-size: 0.95em; }
.auth-error { color: var(--bg-danger); font-size: 0.85em; text-align: center; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 0.85em; color: var(--text-secondary); }
.auth-link { color: var(--bg-accent); font-weight: 500; }
</style>
