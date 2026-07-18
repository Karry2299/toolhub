<template>
  <div class="dash-page">
    <h1 class="section-title">个人仪表盘</h1>
    <div class="metric-grid">
      <div v-for="m in metrics" :key="m.label" class="metric-card">
        <div class="metric-value">{{ m.value }}</div>
        <div class="metric-label">{{ m.label }}</div>
      </div>
    </div>
    <div class="dash-grid">
      <section class="panel card">
        <h2>最近笔记</h2>
        <div v-if="!summary.recent_notes.length" class="empty">暂无笔记</div>
        <router-link v-for="n in summary.recent_notes" :key="n.id" to="/notes" class="row-link">
          <span>{{ n.title }}</span>
          <small>{{ formatDate(n.updated_at) }}</small>
        </router-link>
      </section>
      <section class="panel card">
        <h2>即将提醒</h2>
        <div v-if="!summary.upcoming_reminders.length" class="empty">暂无提醒</div>
        <router-link v-for="r in summary.upcoming_reminders" :key="r.id" to="/productivity?tab=reminders" class="row-link">
          <span>{{ r.title }}</span>
          <small>{{ formatDate(r.remind_at) }}</small>
        </router-link>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { authHeaders } from "../auth.js"

const summary = ref({
  counts: {},
  expense_month_total: "0",
  recent_notes: [],
  upcoming_reminders: [],
})

const metrics = computed(() => [
  { label: "未完成待办", value: summary.value.counts.todos_open || 0 },
  { label: "笔记", value: summary.value.counts.notes || 0 },
  { label: "文件", value: summary.value.counts.files || 0 },
  { label: "书签", value: summary.value.counts.bookmarks || 0 },
  { label: "短链接", value: summary.value.counts.shortlinks || 0 },
  { label: "本月支出", value: "¥" + (summary.value.expense_month_total || "0") },
])

function formatDate(value) {
  return new Date(value).toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })
}

async function loadSummary() {
  const r = await fetch("/api/dashboard/summary/", { headers: authHeaders() })
  if (r.ok) summary.value = await r.json()
}

onMounted(loadSummary)
</script>

<style scoped>
.dash-page { max-width: var(--max-width); margin: 0 auto; }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; margin-bottom: 20px; }
.metric-card { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-md); padding: 18px; }
.metric-value { font-size: 1.6em; font-weight: 700; color: var(--text-primary); }
.metric-label { color: var(--text-secondary); font-size: 0.86em; }
.dash-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.panel { padding: 20px; }
.panel h2 { font-size: 1.05em; margin-bottom: 12px; }
.row-link { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-default); }
.row-link:last-child { border-bottom: none; }
.row-link small, .empty { color: var(--text-tertiary); }
</style>
