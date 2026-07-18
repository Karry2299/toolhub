<template>
  <div class="tools-page">
    <div class="page-head">
      <h1 class="section-title">效率工具</h1>
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: tab === t.key }" @click="tab = t.key">{{ t.label }}</button>
      </div>
    </div>

    <section v-if="tab === 'clipboard'" class="panel card">
      <div class="form-grid">
        <input v-model="clipboardForm.title" class="input" placeholder="标题" />
        <input v-model="clipboardForm.tags" class="input" placeholder="标签，如 code,link" />
        <textarea v-model="clipboardForm.content" class="input wide" rows="4" placeholder="粘贴临时文本、代码或链接"></textarea>
        <label class="check"><input type="checkbox" v-model="clipboardForm.pinned" /> 置顶</label>
        <button class="btn btn-accent" @click="saveClipboard">保存剪贴板</button>
      </div>
      <div class="list">
        <article v-for="item in clipboard" :key="item.id" class="item">
          <div>
            <h3>{{ item.title || "未命名内容" }}</h3>
            <p>{{ item.content }}</p>
            <small>{{ item.tags }}</small>
          </div>
          <div class="actions">
            <button class="icon-btn" @click="copyText(item.content)">复制</button>
            <button class="icon-btn danger" @click="remove('/api/clipboard/', item.id, loadClipboard)">删除</button>
          </div>
        </article>
      </div>
    </section>

    <section v-if="tab === 'bookmarks'" class="panel card">
      <div class="form-grid">
        <input v-model="bookmarkForm.title" class="input" placeholder="标题" />
        <input v-model="bookmarkForm.url" class="input" placeholder="https://example.com" />
        <input v-model="bookmarkForm.category" class="input" placeholder="分类" />
        <input v-model="bookmarkForm.note" class="input" placeholder="备注" />
        <button class="btn btn-accent" @click="saveBookmark">保存书签</button>
      </div>
      <div class="list">
        <article v-for="b in bookmarks" :key="b.id" class="item">
          <div>
            <h3>{{ b.title }}</h3>
            <p>{{ b.url }}</p>
            <small>{{ b.category || "未分类" }} · 打开 {{ b.open_count }} 次</small>
          </div>
          <div class="actions">
            <a class="icon-btn" :href="b.url" target="_blank" @click="markBookmarkOpened(b)">打开</a>
            <button class="icon-btn danger" @click="remove('/api/bookmarks/', b.id, loadBookmarks)">删除</button>
          </div>
        </article>
      </div>
    </section>

    <section v-if="tab === 'reminders'" class="panel card">
      <div class="form-grid">
        <input v-model="reminderForm.title" class="input" placeholder="提醒事项" />
        <input v-model="reminderForm.remind_at" class="input" type="datetime-local" />
        <select v-model="reminderForm.repeat" class="input">
          <option value="">不重复</option>
          <option value="daily">每天</option>
          <option value="weekly">每周</option>
          <option value="monthly">每月</option>
        </select>
        <input v-model="reminderForm.note" class="input" placeholder="备注" />
        <button class="btn btn-accent" @click="saveReminder">保存提醒</button>
      </div>
      <div class="list">
        <article v-for="r in reminders" :key="r.id" class="item">
          <div>
            <h3 :class="{ done: r.completed }">{{ r.title }}</h3>
            <p>{{ formatDate(r.remind_at) }}</p>
            <small>{{ r.repeat || "不重复" }} {{ r.note ? "· " + r.note : "" }}</small>
          </div>
          <div class="actions">
            <button class="icon-btn" @click="toggleReminder(r)">{{ r.completed ? "恢复" : "完成" }}</button>
            <button class="icon-btn danger" @click="remove('/api/reminders/', r.id, loadReminders)">删除</button>
          </div>
        </article>
      </div>
    </section>

    <section v-if="tab === 'shortlinks'" class="panel card">
      <div class="form-grid">
        <input v-model="shortForm.title" class="input" placeholder="标题" />
        <input v-model="shortForm.target_url" class="input" placeholder="目标链接" />
        <input v-model="shortForm.code" class="input" placeholder="自定义短码，可留空" />
        <button class="btn btn-accent" @click="saveShortLink">生成短链接</button>
      </div>
      <div class="list">
        <article v-for="s in shortlinks" :key="s.id" class="item">
          <div>
            <h3>{{ s.title || s.code }}</h3>
            <p>{{ s.short_url }}</p>
            <small>{{ s.target_url }} · 访问 {{ s.visits }} 次</small>
          </div>
          <div class="actions">
            <button class="icon-btn" @click="copyText(s.short_url)">复制</button>
            <button class="icon-btn danger" @click="remove('/api/shortlinks/', s.id, loadShortLinks)">删除</button>
          </div>
        </article>
      </div>
    </section>

    <section v-if="tab === 'expenses'" class="panel card">
      <div class="summary">本页显示最近账本记录，月度汇总可在仪表盘查看。</div>
      <div class="form-grid">
        <input v-model.number="expenseForm.amount" class="input" type="number" step="0.01" placeholder="金额" />
        <input v-model="expenseForm.category" class="input" placeholder="分类" />
        <input v-model="expenseForm.spent_at" class="input" type="date" />
        <input v-model="expenseForm.note" class="input" placeholder="备注" />
        <button class="btn btn-accent" @click="saveExpense">记一笔</button>
      </div>
      <div class="list">
        <article v-for="e in expenses" :key="e.id" class="item compact">
          <div>
            <h3>¥{{ e.amount }} · {{ e.category }}</h3>
            <small>{{ e.spent_at }} {{ e.note ? "· " + e.note : "" }}</small>
          </div>
          <button class="icon-btn danger" @click="remove('/api/expenses/', e.id, loadExpenses)">删除</button>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { authHeaders } from "../auth.js"

const route = useRoute()
const tabs = [
  { key: "clipboard", label: "剪贴板" },
  { key: "bookmarks", label: "书签" },
  { key: "reminders", label: "提醒" },
  { key: "shortlinks", label: "短链接" },
  { key: "expenses", label: "账本" },
]
const tab = ref(route.query.tab || "clipboard")

const clipboard = ref([])
const bookmarks = ref([])
const reminders = ref([])
const shortlinks = ref([])
const expenses = ref([])

const today = new Date().toISOString().slice(0, 10)
const clipboardForm = ref({ title: "", content: "", tags: "", pinned: false })
const bookmarkForm = ref({ title: "", url: "", category: "", note: "" })
const reminderForm = ref({ title: "", remind_at: "", repeat: "", note: "" })
const shortForm = ref({ title: "", target_url: "", code: "" })
const expenseForm = ref({ amount: null, category: "日常", note: "", spent_at: today })

async function getJson(url) {
  const r = await fetch(url, { headers: authHeaders() })
  return r.ok ? await r.json() : []
}

async function postJson(url, body) {
  const r = await fetch(url, { method: "POST", headers: authHeaders(), body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return await r.json()
}

async function patchJson(url, body) {
  await fetch(url, { method: "PATCH", headers: authHeaders(), body: JSON.stringify(body) })
}

async function remove(base, id, reload) {
  await fetch(base + id + "/", { method: "DELETE", headers: authHeaders() })
  await reload()
}

async function loadClipboard() { clipboard.value = await getJson("/api/clipboard/") }
async function loadBookmarks() { bookmarks.value = await getJson("/api/bookmarks/") }
async function loadReminders() { reminders.value = await getJson("/api/reminders/") }
async function loadShortLinks() { shortlinks.value = await getJson("/api/shortlinks/") }
async function loadExpenses() { expenses.value = await getJson("/api/expenses/") }

async function saveClipboard() {
  if (!clipboardForm.value.content.trim()) return
  await postJson("/api/clipboard/", clipboardForm.value)
  clipboardForm.value = { title: "", content: "", tags: "", pinned: false }
  await loadClipboard()
}

async function saveBookmark() {
  if (!bookmarkForm.value.title || !bookmarkForm.value.url) return
  await postJson("/api/bookmarks/", bookmarkForm.value)
  bookmarkForm.value = { title: "", url: "", category: "", note: "" }
  await loadBookmarks()
}

async function markBookmarkOpened(b) {
  fetch("/api/bookmarks/" + b.id + "/opened/", { method: "POST", headers: authHeaders() })
}

async function saveReminder() {
  if (!reminderForm.value.title || !reminderForm.value.remind_at) return
  await postJson("/api/reminders/", reminderForm.value)
  reminderForm.value = { title: "", remind_at: "", repeat: "", note: "" }
  await loadReminders()
}

async function toggleReminder(r) {
  await patchJson("/api/reminders/" + r.id + "/", { completed: !r.completed })
  await loadReminders()
}

async function saveShortLink() {
  if (!shortForm.value.target_url) return
  await postJson("/api/shortlinks/", shortForm.value)
  shortForm.value = { title: "", target_url: "", code: "" }
  await loadShortLinks()
}

async function saveExpense() {
  if (!expenseForm.value.amount) return
  await postJson("/api/expenses/", expenseForm.value)
  expenseForm.value = { amount: null, category: "日常", note: "", spent_at: today }
  await loadExpenses()
}

function copyText(text) {
  navigator.clipboard.writeText(text)
}

function formatDate(value) {
  return new Date(value).toLocaleString("zh-CN")
}

async function loadCurrent() {
  if (tab.value === "clipboard") await loadClipboard()
  if (tab.value === "bookmarks") await loadBookmarks()
  if (tab.value === "reminders") await loadReminders()
  if (tab.value === "shortlinks") await loadShortLinks()
  if (tab.value === "expenses") await loadExpenses()
}

watch(tab, loadCurrent)
onMounted(loadCurrent)
</script>

<style scoped>
.tools-page { max-width: var(--max-width); margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 18px; }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; }
.tab { padding: 8px 14px; border: 1px solid var(--border-default); border-radius: var(--radius-sm); background: var(--bg-card); color: var(--text-secondary); cursor: pointer; }
.tab.active { background: var(--bg-header); color: var(--text-inverse); border-color: var(--bg-header); }
.panel { padding: 20px; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 18px; align-items: start; }
.wide { grid-column: 1 / -1; resize: vertical; }
.check { display: flex; align-items: center; gap: 8px; color: var(--text-secondary); padding: 10px 0; }
.list { display: flex; flex-direction: column; gap: 10px; }
.item { display: flex; justify-content: space-between; gap: 16px; padding: 14px; border: 1px solid var(--border-default); border-radius: var(--radius-sm); background: var(--bg-card-hover); }
.item h3 { font-size: 0.98em; margin-bottom: 4px; }
.item p { color: var(--text-secondary); font-size: 0.86em; word-break: break-all; white-space: pre-wrap; }
.item small, .summary { color: var(--text-tertiary); }
.compact { align-items: center; }
.actions { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }
.icon-btn { border: 1px solid var(--border-default); background: var(--bg-card); color: var(--text-secondary); border-radius: var(--radius-sm); padding: 7px 10px; cursor: pointer; white-space: nowrap; }
.icon-btn.danger { color: var(--bg-danger); }
.done { text-decoration: line-through; color: var(--text-tertiary); }
@media (max-width: 760px) {
  .page-head, .item { flex-direction: column; align-items: stretch; }
  .actions { justify-content: flex-start; }
}
</style>
