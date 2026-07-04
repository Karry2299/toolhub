<template>
  <div class="fm-page">
    <div class="fm-header">
      <h2 class="fm-title">📁 文件管理器</h2>
      <label class="upload-btn">
        上传文件
        <input type="file" @change="startUpload" hidden />
      </label>
    </div>

    <!-- Upload Queue -->
    <div v-if="uploadQueue.length" class="upload-queue">
      <div v-for="(item, i) in uploadQueue" :key="i" class="upload-item">
        <div class="upload-info">
          <span class="upload-name">{{ item.name }}</span>
          <span class="upload-size">{{ item.size }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{width: item.progress+'%', background: item.done ? '#22c55e' : item.error ? '#ef4444' : '#3b82f6'}"></div>
        </div>
        <div class="upload-status">
          <span v-if="item.done" class="status-done">✅ 完成</span>
          <span v-else-if="item.error" class="status-err">❌ {{ item.error }}</span>
          <span v-else class="status-progress">{{ item.progress }}%</span>
        </div>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="fm-tabs">
      <button class="tab-btn" :class="{active:tab==='all'}" @click="tab='all'">全部 ({{ files.length }})</button>
      <button class="tab-btn" :class="{active:tab==='fav'}" @click="tab='fav'">⭐ 收藏 ({{ favCount }})</button>
    </div>

    <!-- File Grid -->
    <div v-if="loading" class="fm-state">加载中...</div>
    <div v-else-if="!list.length" class="fm-state">暂无文件，点击上方按钮上传</div>
    <div v-else class="fm-grid">
      <div v-for="f in list" :key="f.id" class="file-card">
        <div class="file-icon">{{ f.file_icon || '📎' }}</div>
        <div class="file-name" :title="f.original_filename">{{ truncate(f.original_filename, 22) }}</div>
        <div class="file-meta">{{ f.size_display }}</div>
        <div class="file-actions">
          <a :href="f.download_url || '/api/files/'+f.id+'/download/'" class="action-btn" title="下载" download>⬇️</a>
          <button @click="toggleFav(f)" class="action-btn" :class="{fav:f.is_favorite}" title="收藏">⭐</button>
          <button @click="shareFile(f)" class="action-btn" title="分享">🔗</button>
          <button @click="deleteFile(f)" class="action-btn del" title="删除">✖️</button>
        </div>
        <div v-if="f.is_favorite" class="fav-badge">⭐</div>
      </div>
    </div>

    <!-- Share Modal -->
    <div v-if="shareUrl" class="modal-overlay" @click="shareUrl=''">
      <div class="modal-box" @click.stop>
        <h3>分享文件</h3>
        <div class="share-link">{{ shareUrl }}</div>
        <button @click="copyShare" class="btn-copy">📋 复制链接</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { authHeaders, authUploadHeaders } from "../auth.js"

const API = "/api/files/"
const files = ref([])
const loading = ref(true)
const tab = ref("all")
const shareUrl = ref("")
const uploadQueue = ref([])

const favCount = computed(() => files.value.filter(f => f.is_favorite).length)
const list = computed(() => tab.value === "fav" ? files.value.filter(f => f.is_favorite) : files.value)

function truncate(name, max) { return name.length > max ? name.slice(0, max) + "..." : name }

function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B"
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + " KB"
  return (bytes/(1024*1024)).toFixed(1) + " MB"
}

async function fetchFiles() {
  loading.value = true
  try {
    const r = await fetch(API, { headers: authHeaders() })
    if (r.ok) files.value = await r.json()
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function startUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  e.target.value = ""

  const item = { name: file.name, size: formatSize(file.size), progress: 0, done: false, error: null }
  uploadQueue.value.push(item)

  const form = new FormData()
  form.append("file", file)

  const xhr = new XMLHttpRequest()

  xhr.upload.onprogress = (ev) => {
    if (ev.lengthComputable) {
      item.progress = Math.round((ev.loaded / ev.total) * 100)
    }
  }

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      item.done = true
      item.progress = 100
      try {
        const data = JSON.parse(xhr.responseText)
        files.value.unshift(data)
      } catch (e) {
        fetchFiles()
      }
      setTimeout(() => { uploadQueue.value = uploadQueue.value.filter(x => x !== item) }, 3000)
    } else {
      item.error = "上传失败 (" + xhr.status + ")"
    }
  }

  xhr.onerror = () => { item.error = "网络错误" }
  xhr.ontimeout = () => { item.error = "上传超时" }

  xhr.open("POST", API)
  const headers = authUploadHeaders()
  for (const [k, v] of Object.entries(headers)) xhr.setRequestHeader(k, v)
  xhr.send(form)
}

async function toggleFav(f) {
  try {
    const r = await fetch(API + f.id + "/favorite/", { method: "POST", headers: authHeaders() })
    if (r.ok) {
      const data = await r.json()
      f.is_favorite = data.is_favorite
    }
  } catch (e) { console.error(e) }
}

async function deleteFile(f) {
  if (!confirm("确定删除 " + f.original_filename + "？")) return
  try {
    await fetch(API + f.id + "/", { method: "DELETE", headers: authHeaders() })
    files.value = files.value.filter(x => x.id !== f.id)
  } catch (e) { console.error(e) }
}

async function shareFile(f) {
  shareUrl.value = window.location.origin + "/api/files/shared/" + f.share_token + "/"
}

function copyShare() {
  navigator.clipboard.writeText(shareUrl.value).then(() => alert("已复制分享链接"))
}

onMounted(fetchFiles)
</script>

<style scoped>
.fm-page { max-width:var(--max-width); margin:0 auto; padding:0 24px 40px; }
.fm-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; }
.fm-title { font-size:1.3em; font-weight:700; color:var(--text-primary); }
.upload-btn { display:inline-flex; padding:10px 24px; border:none; border-radius:var(--radius-sm); background:linear-gradient(135deg,#3b82f6,#2563eb); color:#fff; font-size:0.9em; font-weight:500; cursor:pointer; transition:all 0.2s; }
.upload-btn:hover { box-shadow:var(--shadow-md); transform:translateY(-1px); }

/* Upload Queue */
.upload-queue { margin-bottom:20px; display:flex; flex-direction:column; gap:8px; }
.upload-item { background:var(--bg-card); border:1px solid var(--border-default); border-radius:var(--radius-md); padding:12px 16px; display:flex; align-items:center; gap:12px; }
.upload-info { flex:1; min-width:0; }
.upload-name { font-size:0.85em; font-weight:500; color:var(--text-primary); display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.upload-size { font-size:0.75em; color:var(--text-tertiary); }
.progress-bar { flex:1; max-width:200px; height:6px; background:#e5e7eb; border-radius:3px; overflow:hidden; }
.progress-fill { height:100%; border-radius:3px; transition:width 0.3s ease; }
.upload-status { min-width:60px; text-align:right; font-size:0.82em; }
.status-done { color:#22c55e; }
.status-err { color:#ef4444; font-size:0.78em; }
.status-progress { color:#3b82f6; font-weight:500; }

/* Tabs */
.fm-tabs { display:flex; gap:8px; margin-bottom:20px; }
.tab-btn { padding:8px 18px; border:1px solid var(--border-default); border-radius:var(--radius-sm); background:transparent; color:var(--text-secondary); font-size:0.85em; cursor:pointer; transition:all 0.2s; }
.tab-btn:hover { border-color:var(--text-tertiary); color:var(--text-primary); }
.tab-btn.active { background:var(--bg-header); color:var(--text-inverse); border-color:var(--bg-header); }

/* Grid */
.fm-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:16px; }
.file-card { position:relative; background:var(--bg-card); border:1px solid var(--border-default); border-radius:var(--radius-lg); padding:24px 16px 20px; text-align:center; transition:all 0.2s; }
.file-card:hover { box-shadow:var(--shadow-lg); border-color:transparent; transform:translateY(-2px); }
.file-icon { font-size:2.4em; margin-bottom:10px; }
.file-name { font-size:0.83em; color:var(--text-primary); word-break:break-all; margin-bottom:4px; }
.file-meta { font-size:0.75em; color:var(--text-tertiary); margin-bottom:14px; }
.file-actions { display:flex; gap:4px; justify-content:center; }
.action-btn { width:34px; height:34px; display:inline-flex; align-items:center; justify-content:center; border:1px solid var(--border-default); border-radius:var(--radius-sm); background:transparent; cursor:pointer; font-size:0.8em; transition:all 0.2s; text-decoration:none; color:var(--text-secondary); }
.action-btn:hover { border-color:var(--text-tertiary); background:var(--bg-card-hover); }
.action-btn.fav { color:var(--bg-accent); border-color:var(--bg-accent); background:rgba(245,158,11,0.06); }
.action-btn.del:hover { color:var(--bg-danger); border-color:var(--bg-danger); }
.fav-badge { position:absolute; top:8px; right:8px; font-size:0.85em; }
.fm-state { text-align:center; padding:60px 0; color:var(--text-tertiary); font-size:0.9em; }

/* Share Modal */
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:999; }
.modal-box { background:var(--bg-card); border-radius:var(--radius-lg); padding:28px; max-width:420px; width:90%; }
.modal-box h3 { font-size:1.05em; font-weight:600; margin-bottom:12px; color:var(--text-primary); }
.share-link { padding:10px 12px; background:#f8fafc; border:1px solid var(--border-default); border-radius:var(--radius-sm); font-size:0.85em; color:var(--text-primary); word-break:break-all; margin-bottom:12px; }
.btn-copy { padding:10px 20px; border:none; border-radius:var(--radius-sm); background:var(--bg-accent); color:#fff; font-size:0.88em; cursor:pointer; }
.btn-copy:hover { background:var(--bg-accent-hover); }
</style>