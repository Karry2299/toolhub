import fs from "fs";

// Login.vue
const login = `<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <h1 class="auth-logo">\u25c6 ToolHub</h1>
        <p class="auth-desc">\u767b\u5f55\u4f60\u7684\u8d26\u6237</p>
      </div>
      <form @submit.prevent="login" class="auth-form">
        <div class="field">
          <label>\u7528\u6237\u540d</label>
          <input v-model="username" class="input" placeholder="\u8f93\u5165\u7528\u6237\u540d" required />
        </div>
        <div class="field">
          <label>\u5bc6\u7801</label>
          <input v-model="password" type="password" class="input" placeholder="\u8f93\u5165\u5bc6\u7801" required />
        </div>
        <p v-if="error" class="auth-error">{{ error }}</p>
        <button type="submit" class="btn btn-accent auth-btn" :disabled="loading">{{ loading ? "\u767b\u5f55\u4e2d..." : "\u767b\u5f55" }}</button>
      </form>
      <p class="auth-footer">\u8fd8\u6ca1\u6709\u8d26\u53f7\uff1f <router-link to="/register" class="auth-link">\u7acb\u5373\u6ce8\u518c</router-link></p>
    </div>
  </div>
</template>
<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { auth } from "../auth.js"
const router = useRouter()
const username = ref(""); const password = ref(""); const error = ref(""); const loading = ref(false)
async function login() {
  error.value = ""; loading.value = true
  try {
    const r = await fetch("/api/auth/login/", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({username: username.value, password: password.value}) })
    const data = await r.json()
    if (r.ok) {
      auth.login(data.token, {username: data.username, id: data.user_id})
      router.push("/")
    } else {
      error.value = data.error || "\u767b\u5f55\u5931\u8d25"
    }
  } catch(e) { error.value = "\u7f51\u7edc\u9519\u8bef" }
  finally { loading.value = false }
}
</script>
<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 200px); }
.auth-card { padding: 40px; max-width: 380px; width: 100%; }
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-logo { font-size: 1.6em; font-weight: 700; color: var(--text-primary); }
.auth-desc { font-size: 0.9em; color: var(--text-secondary); margin-top: 6px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 0.85em; font-weight: 500; color: var(--text-secondary); }
.auth-btn { width: 100%; padding: 12px; justify-content: center; font-size: 0.95em; }
.auth-error { color: var(--bg-danger); font-size: 0.85em; text-align: center; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 0.85em; color: var(--text-secondary); }
.auth-link { color: var(--bg-accent); font-weight: 500; }
</style>`;

const register = `<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <h1 class="auth-logo">\u25c6 ToolHub</h1>
        <p class="auth-desc">\u521b\u5efa\u65b0\u8d26\u6237</p>
      </div>
      <form @submit.prevent="register" class="auth-form">
        <div class="field">
          <label>\u7528\u6237\u540d</label>
          <input v-model="username" class="input" placeholder="\u8f93\u5165\u7528\u6237\u540d" required />
        </div>
        <div class="field">
          <label>\u5bc6\u7801</label>
          <input v-model="password" type="password" class="input" placeholder="\u8f93\u5165\u5bc6\u7801\uff08\u81f3\u5c116\u4f4d\uff09" required minlength="6" />
        </div>
        <div class="field">
          <label>\u786e\u8ba4\u5bc6\u7801</label>
          <input v-model="confirmPwd" type="password" class="input" placeholder="\u518d\u6b21\u8f93\u5165\u5bc6\u7801" required />
        </div>
        <p v-if="error" class="auth-error">{{ error }}</p>
        <button type="submit" class="btn btn-accent auth-btn" :disabled="loading">{{ loading ? "\u6ce8\u518c\u4e2d..." : "\u6ce8\u518c" }}</button>
      </form>
      <p class="auth-footer">\u5df2\u6709\u8d26\u53f7\uff1f <router-link to="/login" class="auth-link">\u7acb\u5373\u767b\u5f55</router-link></p>
    </div>
  </div>
</template>
<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { auth } from "../auth.js"
const router = useRouter()
const username = ref(""); const password = ref(""); const confirmPwd = ref(""); const error = ref(""); const loading = ref(false)
async function register() {
  error.value = ""
  if (password.value !== confirmPwd.value) { error.value = "\u4e24\u6b21\u5bc6\u7801\u4e0d\u4e00\u81f4"; return }
  loading.value = true
  try {
    const r = await fetch("/api/auth/register/", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({username: username.value, password: password.value}) })
    const data = await r.json()
    if (r.ok) {
      auth.login(data.token, {username: data.username, id: data.user_id})
      router.push("/")
    } else {
      error.value = data.error || "\u6ce8\u518c\u5931\u8d25"
    }
  } catch(e) { error.value = "\u7f51\u7edc\u9519\u8bef" }
  finally { loading.value = false }
}
</script>
<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 200px); }
.auth-card { padding: 40px; max-width: 380px; width: 100%; }
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-logo { font-size: 1.6em; font-weight: 700; color: var(--text-primary); }
.auth-desc { font-size: 0.9em; color: var(--text-secondary); margin-top: 6px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 0.85em; font-weight: 500; color: var(--text-secondary); }
.auth-btn { width: 100%; padding: 12px; justify-content: center; font-size: 0.95em; }
.auth-error { color: var(--bg-danger); font-size: 0.85em; text-align: center; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 0.85em; color: var(--text-secondary); }
.auth-link { color: var(--bg-accent); font-weight: 500; }
</style>`;

fs.writeFileSync("src/views/Login.vue", login, "utf-8");
fs.writeFileSync("src/views/Register.vue", register, "utf-8");
console.log("Login.vue and Register.vue created");