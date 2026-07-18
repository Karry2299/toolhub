<template>
  <div class="pwd-gen page-container">
    <h2 class="section-title">密码生成器</h2>

    <div class="pwd-generator card">
      <div class="pwd-display">
        <input :value="password" readonly class="input pwd-output" />
        <button @click="copyPwd" class="btn btn-accent">复制</button>
        <button @click="showSave = true" class="btn btn-primary">保存</button>
      </div>

      <div class="pwd-options">
        <label class="option-row">
          <span class="option-label">密码长度</span>
          <input type="range" v-model.number="length" min="4" max="64" class="option-slider" />
          <span class="option-value">{{ length }}</span>
        </label>
        <label class="option-row"><input type="checkbox" v-model="useUpper" class="option-check" /><span>大写字母 (A-Z)</span></label>
        <label class="option-row"><input type="checkbox" v-model="useLower" class="option-check" /><span>小写字母 (a-z)</span></label>
        <label class="option-row"><input type="checkbox" v-model="useDigits" class="option-check" /><span>数字 (0-9)</span></label>
        <label class="option-row"><input type="checkbox" v-model="useSymbols" class="option-check" /><span>特殊字符 (!@#$%^&*)</span></label>
      </div>

      <button @click="generate" class="btn btn-accent" style="margin-top:12px;width:100%">重新生成</button>

      <div class="pwd-strength" v-if="password">
        密码强度：<span :class="strengthClass">{{ strengthText }}</span>
      </div>
    </div>

    <div v-if="showSave" class="share-modal" @click="showSave = false">
      <div class="share-box card" @click.stop>
        <h3>保存密码</h3>
        <div class="saved-pwd-display">{{ password }}</div>
        <textarea v-model="saveNote" class="input" rows="3" placeholder="添加备注说明（可选）"></textarea>
        <div class="dialog-actions">
          <button @click="showSave = false" class="btn btn-ghost">取消</button>
          <button @click="savePassword" class="btn btn-accent">保存</button>
        </div>
      </div>
    </div>

    <div class="saved-section" v-if="savedPasswords.length > 0">
      <h3 class="sub-title">已保存的密码</h3>
      <div class="saved-list">
        <div v-for="item in savedPasswords" :key="item.id" class="saved-item card">
          <div class="saved-item-header">
            <span class="saved-pwd">{{ item.password }}</span>
            <button @click="deleteSaved(item.id)" class="btn btn-ghost action-btn" title="删除">&#x2716;</button>
          </div>
          <div class="saved-item-meta">
            <span v-if="item.note" class="saved-note">{{ item.note }}</span>
            <span class="saved-time">{{ formatTime(item.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { authHeaders } from "../auth.js"

const password = ref("")
const length = ref(16)
const useUpper = ref(true)
const useLower = ref(true)
const useDigits = ref(true)
const useSymbols = ref(true)
const showSave = ref(false)
const saveNote = ref("")
const savedPasswords = ref([])
const API = "/api/passwords/"

function generate() {
  let chars = ""
  if (useUpper.value) chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  if (useLower.value) chars += "abcdefghijklmnopqrstuvwxyz"
  if (useDigits.value) chars += "0123456789"
  if (useSymbols.value) chars += "!@#$%^&*()_+{}[]:;<>,.?/~"
  if (!chars) {
    password.value = "请至少选择一种字符类型"
    return
  }
  let result = ""
  for (let i = 0; i < length.value; i++) result += chars[Math.floor(Math.random() * chars.length)]
  password.value = result
}

async function copyPwd() {
  try {
    await navigator.clipboard.writeText(password.value)
    alert("已复制到剪贴板")
  } catch (e) {
    console.error(e)
  }
}

async function savePassword() {
  try {
    const body = {
      password: password.value,
      length: length.value,
      has_upper: useUpper.value,
      has_lower: useLower.value,
      has_digits: useDigits.value,
      has_symbols: useSymbols.value,
      note: saveNote.value,
    }
    const r = await fetch(API, { method: "POST", headers: authHeaders(), body: JSON.stringify(body) })
    if (r.ok) {
      const saved = await r.json()
      savedPasswords.value.unshift(saved)
      showSave.value = false
      saveNote.value = ""
      alert("密码已保存")
    }
  } catch (e) {
    console.error(e)
  }
}

async function deleteSaved(id) {
  try {
    await fetch(API + id + "/", { method: "DELETE", headers: authHeaders() })
    savedPasswords.value = savedPasswords.value.filter(x => x.id !== id)
  } catch (e) {
    console.error(e)
  }
}

function formatTime(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })
}

const strengthClass = computed(() => {
  const l = password.value.length
  if (l < 8) return "strength-weak"
  if (l < 12) return "strength-medium"
  if (l < 16) return "strength-strong"
  return "strength-vstrong"
})

const strengthText = computed(() => {
  const l = password.value.length
  if (l < 8) return "弱"
  if (l < 12) return "中等"
  if (l < 16) return "强"
  return "非常强"
})

async function fetchSaved() {
  try {
    const r = await fetch(API, { headers: authHeaders() })
    savedPasswords.value = await r.json()
  } catch (e) {
    console.error(e)
  }
}

generate()
onMounted(fetchSaved)
</script>

<style scoped>
.pwd-gen { max-width: 560px; margin: 0 auto; }
.pwd-generator { padding: 28px; }
.pwd-display { display: flex; gap: 10px; margin-bottom: 24px; }
.pwd-output { flex: 1; font-family: "SF Mono", "Fira Code", monospace; font-size: 1.1em; text-align: center; letter-spacing: 0.05em; }
.pwd-options { display: flex; flex-direction: column; gap: 14px; }
.option-row { display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: 0.9em; color: var(--text-secondary); }
.option-label { min-width: 72px; }
.option-slider { flex: 1; accent-color: var(--bg-accent); }
.option-value { min-width: 28px; text-align: right; font-weight: 600; color: var(--text-primary); }
.option-check { accent-color: var(--bg-accent); width: 16px; height: 16px; }
.pwd-strength { margin-top: 16px; text-align: center; font-size: 0.95em; color: var(--text-secondary); }
.strength-weak { color: var(--bg-danger); }
.strength-medium { color: var(--bg-accent); }
.strength-strong { color: var(--bg-success); }
.strength-vstrong { color: var(--bg-success); font-weight: 700; }
.sub-title { font-size: 1.1em; font-weight: 600; margin: 32px 0 16px; color: var(--text-primary); }
.saved-list { display: flex; flex-direction: column; gap: 10px; }
.saved-item { padding: 14px 18px; }
.saved-item-header { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.saved-pwd { font-family: "SF Mono", "Fira Code", monospace; font-size: 0.85em; letter-spacing: 0.03em; word-break: break-all; }
.saved-item-meta { display: flex; gap: 12px; margin-top: 6px; font-size: 0.8em; color: var(--text-tertiary); }
.saved-note { color: var(--text-secondary); }
.saved-time { white-space: nowrap; }
.action-btn { width: 32px; height: 32px; padding: 0; display: inline-flex; align-items: center; justify-content: center; }
.share-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 999; }
.share-box { padding: 24px; max-width: 420px; width: 90%; display: flex; flex-direction: column; gap: 14px; }
.share-box h3 { font-size: 1.1em; font-weight: 600; }
.saved-pwd-display { font-family: monospace; padding: 10px; background: var(--bg-body); border-radius: var(--radius-sm); text-align: center; font-size: 0.95em; word-break: break-all; letter-spacing: 0.03em; }
.dialog-actions { display: flex; gap: 10px; justify-content: flex-end; }
</style>
