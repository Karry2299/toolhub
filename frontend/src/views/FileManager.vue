<template>
  <div class="file-manager page-container">
    <h2 class="section-title">文件管理器</h2>
    <div class="fm-toolbar">
      <label class="btn btn-primary upload-btn">上传文件<input type="file" @change="uploadFile" hidden /></label>
      <div class="fm-tabs">
        <button class="btn btn-ghost filter-btn" :class="{active: tab === 'all'}" @click="tab='all'">全部</button>
        <button class="btn btn-ghost filter-btn" :class="{active: tab === 'fav'}" @click="tab='fav'">收藏</button>
      </div>
    </div>
    <div v-if="loading" class="fm-loading">加载中...</div>
    <div v-else class="fm-grid">
      <div v-for="f in filteredFiles" :key="f.id" class="file-card card">
        <div class="file-icon">{{ fileIcon(f.file_type) }}</div>
        <div class="file-name" :title="f.original_filename">{{ f.original_filename.substring(0, 25) }}{{ f.original_filename.length > 25 ? "..." : "" }}</div>
        <div class="file-meta">{{ f.size_display }}</div>
        <div class="file-actions">
          <a :href="'/api/files/'+f.id+'/download/'" class="btn btn-ghost action-btn" title="下载">&#x2B07;</a>
          <button @click="toggleFav(f)" class="btn btn-ghost action-btn" :class="{fav: f.is_favorite}" title="收藏">&#x2B50;</button>
          <button @click="shareFile(f)" class="btn btn-ghost action-btn" title="分享">&#x1F517;</button>
          <button @click="deleteFile(f)" class="btn btn-ghost action-btn del" title="删除">&#x2716;</button>
        </div>
      </div>
    </div>
    <div v-if="!loading && filteredFiles.length===0" class="fm-empty">暂无文件</div>
    <div v-if="shareUrl" class="share-modal" @click="closeShare">
      <div class="share-box card" @click.stop>分享链接<textarea readonly>{{ shareUrl }}</textarea><button @click="copyShare" class="btn btn-accent">复制</button></div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from "vue"
import { authHeaders, authUploadHeaders } from "../auth.js"
const files = ref([]); const loading = ref(true); const tab = ref("all"); const shareUrl = ref("")
const API = "/api/files/"
const filteredFiles = computed(() => tab.value === "fav" ? files.value.filter(f => f.is_favorite) : files.value)
function fileIcon(type) {
  if (!type) return "📫"
  if (type.startsWith("image/")) return "🖼"
  if (type.startsWith("video/")) return "🎴"
  if (type.startsWith("audio/")) return "🎍"
  if (type.includes("pdf")) return "📵"
  if (type.includes("zip") || type.includes("rar") || type.includes("tar")) return "📝"
  if (type.includes("text") || type.includes("document")) return "📑"
  return "📫"
}
async function fetchFiles() {
  try { const r = await fetch(API, { headers: authHeaders() }); files.value = await r.json() }
  catch(e) { console.error(e) }
  finally { loading.value = false }
}
async function uploadFile(e) {
  const file = e.target.files[0]; if (!file) return
  const form = new FormData(); form.append("file", file)
  try {
    const r = await fetch(API, { method: "POST", headers: authUploadHeaders(), body: form })
    if (r.ok) { files.value.unshift(await r.json()) }
  } catch(e) { console.error(e) }
  e.target.value = ""
}
async function toggleFav(f) {
  try { await fetch(API + f.id + "/favorite/", { method: "POST", headers: authHeaders() }) }
  catch(e) { console.error(e) }
}
async function deleteFile(f) {
  if (!confirm("确定删除 " + f.original_filename + "？")) return
  try {
    await fetch(API + f.id + "/", { method: "DELETE", headers: authHeaders() })
    files.value = files.value.filter(x => x.id !== f.id)
  } catch(e) { console.error(e) }
}
async function shareFile(f) {
  shareUrl.value = window.location.origin + "/api/files/shared/" + f.share_token + "/"
}
function copyShare() {
  navigator.clipboard.writeText(shareUrl.value).then(() => alert("已复制分享链接"))
}
function closeShare() { shareUrl.value = "" }
onMounted(fetchFiles)
</script>
<style scoped>
.fm-toolbar { display: flex; gap: 15px; align-items: center; margin-bottom: 24px; }
.fm-tabs { display: flex; gap: 8px; }
.fm-tabs .btn.active { background: var(--bg-header); color: var(--text-inverse); border-color: var(--bg-header); }
.fm-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.file-card { padding: 24px 16px 20px; text-align: center; }
.file-icon { font-size: 2.5em; margin-bottom: 10px; }
.file-name { font-size: 0.85em; word-break: break-all; margin-bottom: 4px; color: var(--text-primary); }
.file-meta { font-size: 0.75em; color: var(--text-tertiary); margin-bottom: 14px; }
.file-actions { display: flex; gap: 6px; justify-content: center; }
.action-btn { width: 36px; height: 36px; padding: 0; }
.action-btn.fav { color: var(--bg-accent); border-color: var(--bg-accent); }
.action-btn.del:hover { color: var(--bg-danger); border-color: var(--bg-danger); }
.fm-loading, .fm-empty { text-align: center; padding: 60px; color: var(--text-tertiary); }
.share-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 999; }
.share-box { padding: 24px; max-width: 400px; width: 90%; display: flex; flex-direction: column; gap: 12px; }
.share-box textarea { width: 100%; padding: 8px; border: 1px solid var(--border-default); border-radius: var(--radius-sm); resize: none; font-size: 0.85em; }
</style>
