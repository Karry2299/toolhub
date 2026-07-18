<template>
  <div class="ip-lookup">
    <h2 class="section-title">IP / 域名查询</h2>
    <div class="ip-form">
      <input v-model="query" @keyup.enter="lookup" placeholder="输入 IP 地址或域名..." class="ip-input" />
      <button @click="lookup" class="btn-primary">查询</button>
    </div>
    <div v-if="loading" class="ip-loading">查询中...</div>
    <div v-if="result" class="ip-result">
      <div class="result-row"><span class="label">IP:</span><span>{{ result.ip }}</span></div>
      <div class="result-row"><span class="label">国家:</span><span>{{ result.country }}</span></div>
      <div class="result-row"><span class="label">省份:</span><span>{{ result.region }}</span></div>
      <div class="result-row"><span class="label">城市:</span><span>{{ result.city }}</span></div>
      <div class="result-row"><span class="label">运营商:</span><span>{{ result.org }}</span></div>
    </div>
    <div v-if="error" class="ip-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const query = ref("")
const result = ref(null)
const loading = ref(false)
const error = ref("")

async function lookup() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ""
  result.value = null
  try {
    const r = await fetch("/api/ip-lookup/?q=" + encodeURIComponent(query.value))
    if (!r.ok) {
      const e = await r.json()
      error.value = e.error
      return
    }
    result.value = await r.json()
  } catch (e) {
    error.value = "查询失败"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.ip-lookup { max-width: 500px; margin: 0 auto; }
.ip-form { display: flex; gap: 10px; margin-bottom: 20px; }
.ip-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 1em; }
.ip-loading { text-align: center; color: #95a5a6; padding: 20px; }
.ip-result { background: #fff; border-radius: 8px; padding: 20px; border: 1px solid #eee; }
.result-row { display: flex; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.result-row:last-child { border-bottom: none; }
.label { min-width: 80px; font-weight: 600; color: #555; }
.ip-error { color: #e74c3c; text-align: center; padding: 20px; }
</style>
