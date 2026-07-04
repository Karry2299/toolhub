<template>
  <div class="file-tools-page">
    <div class="page-header">
      <h1 class="page-title">📄 文档处理工具</h1>
      <p class="page-desc">PDF 转 Word、合并拆分、文档格式转换</p>
    </div>

    <!-- 转换类型选择 -->
    <div class="conv-grid">
      <div v-for="tool in tools" :key="tool.type" class="conv-card" :class="{ active: activeTool === tool.type }" @click="activeTool = tool.type">
        <div class="conv-icon">{{ tool.icon }}</div>
        <div class="conv-name">{{ tool.name }}</div>
      </div>
    </div>

    <!-- 转换面板 -->
    <div class="conv-panel" v-if="activeTool">
      <div class="panel-header">
        <h2 class="panel-title">{{ currentTool?.icon }} {{ currentTool?.name }}</h2>
        <p class="panel-desc">{{ currentTool?.desc }}</p>
      </div>

      <div class="panel-body">
        <!-- 从已上传文件选择 -->
        <div class="upload-area" @drop.prevent="handleDrop" @dragover.prevent>
          <input type="file" ref="fileInput" :accept="currentTool?.accept" hidden multiple @change="handleFileSelect" />
          <div class="upload-placeholder" @click="triggerUpload()">
            <div class="upload-icon">📁</div>
            <div class="upload-text">点击或拖拽文件到此处</div>
            <div class="upload-hint">{{ currentTool?.hint }}</div>
          </div>
        </div>

        <!-- 已选文件列表 -->
        <div v-if="selectedFiles.length" class="file-list">
          <div v-for="(f, i) in selectedFiles" :key="i" class="file-item">
            <span class="file-item-name">📄 {{ f.name }}</span>
            <span class="file-item-size">{{ formatSize(f.size) }}</span>
            <button class="btn-icon" @click="selectedFiles.splice(i, 1)">✕</button>
          </div>
        </div>

        <!-- 拆分的页码输入 -->
        <div v-if="activeTool === 'split_pdf'" class="extra-option">
          <label>页码（多个用逗号分隔，如 1,3,5）：</label>
          <input v-model="splitPages" class="input-field" placeholder="1,3,5" />
        </div>

        <!-- 转换按钮 -->
        <button v-if="selectedFiles.length" class="btn-convert" :disabled="converting" @click="startConvert">
          {{ converting ? "⏳ 转换中..." : "🚀 开始转换" }}
        </button>
      </div>

      <!-- 转换结果 -->
      <div v-if="resultMsg" class="result-bar" :class="resultOk ? 'success' : 'error'">
        <span>{{ resultMsg }}</span>
        <a v-if="downloadUrl" :href="downloadUrl" class="btn-download" download>⬇ 下载</a>
      </div>

      <!-- 转换历史 -->
      <div v-if="conversions.length" class="history-section">
        <h3 class="section-title">📋 转换记录</h3>
        <div v-for="c in conversions" :key="c.id" class="history-item">
          <div class="history-info">
            <span class="history-type">{{ c.conv_type_display }}</span>
            <span class="history-file">{{ c.original_name }}</span>
            <span class="history-status" :class="c.status">{{ c.status === 'completed' ? '✅' : c.status === 'failed' ? '❌' : '⏳' }} {{ c.status }}</span>
          </div>
          <a v-if="c.download_url" :href="c.download_url" class="btn-sm">⬇ 下载</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { auth } from "../auth.js"

const activeTool = ref("pdf2word")
const selectedFiles = ref([])
const converting = ref(false)
const resultMsg = ref("")
const resultOk = ref(false)
const downloadUrl = ref("")
const splitPages = ref("1")
const conversions = ref([])

const tools = [
  { type: "pdf2word", name: "PDF转Word", icon: "📝", accept: ".pdf", hint: "支持 .pdf 文件", desc: "将 PDF 文件转换为可编辑的 Word 文档" },
  { type: "pdf2txt", name: "PDF提取文本", icon: "📃", accept: ".pdf", hint: "支持 .pdf 文件", desc: "从 PDF 中提取纯文本内容" },
  { type: "pdf2images", name: "PDF转图片", icon: "🖼", accept: ".pdf", hint: "支持 .pdf 文件", desc: "将 PDF 每页转为 PNG 图片并打包" },
  { type: "merge_pdf", name: "合并PDF", icon: "🔗", accept: ".pdf", hint: "可多选多个 PDF 文件", desc: "将多个 PDF 文件合并为一个" },
  { type: "split_pdf", name: "拆分PDF", icon: "✂️", accept: ".pdf", hint: "指定页码拆分", desc: "按指定页码拆分 PDF" },
  { type: "word2pdf", name: "Word转PDF", icon: "📄", accept: ".doc,.docx", hint: "支持 .doc/.docx 文件", desc: "将 Word 文档转换为 PDF" },
  { type: "excel2csv", name: "Excel转CSV", icon: "📊", accept: ".xls,.xlsx", hint: "支持 .xls/.xlsx 文件", desc: "将 Excel 表格转换为 CSV 格式" },
  { type: "excel2json", name: "Excel转JSON", icon: "📋", accept: ".xls,.xlsx", hint: "支持 .xls/.xlsx 文件", desc: "将 Excel 表格转换为 JSON 格式" },
]

const currentTool = computed(() => tools.find(t => t.type === activeTool.value))

function handleFileSelect(e) {
  for (const file of e.target.files) {
    if (!selectedFiles.value.find(f => f.name === file.name)) {
      selectedFiles.value.push(file)
    }
  }
}

function triggerUpload() {
  const el = document.querySelector('input[type=file]')
  if (el) el.click()
}

function handleDrop(e) {
  for (const file of e.dataTransfer.files) {
    if (!selectedFiles.value.find(f => f.name === file.name)) {
      selectedFiles.value.push(file)
    }
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + "B"
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + "KB"
  return (bytes / 1024 / 1024).toFixed(1) + "MB"
}

async function startConvert() {
  converting.value = true
  resultMsg.value = ""
  downloadUrl.value = ""
  const form = new FormData()
  form.append("conv_type", activeTool.value)

  if (activeTool.value === "split_pdf") {
    form.append("page", splitPages.value)
  }

  for (const f of selectedFiles.value) {
    form.append("file", f)
  }

  function getCSRFToken() {
    const m = document.cookie.match(/csrftoken=([^;]+)/)
    return m ? m[1] : ""
  }
  try {
    const res = await fetch("/api/filetools/convert/", {
      method: "POST",
      headers: { "Authorization": "Token " + auth.token, "X-CSRFToken": getCSRFToken() },
      body: form,
    })
    const data = await res.json()
    if (data.success) {
      resultOk.value = true
      resultMsg.value = data.message
      if (data.download_url) downloadUrl.value = data.download_url
      selectedFiles.value = []
      fetchConversions()
    } else {
      resultOk.value = false
      resultMsg.value = data.error || "转换失败"
    }
  } catch (e) {
    resultOk.value = false
    resultMsg.value = "请求失败: " + e.message
  } finally {
    converting.value = false
  }
}

async function fetchConversions() {
  try {
    const res = await fetch("/api/filetools/conversions/", {
      headers: { "Authorization": "Token " + auth.token },
    })
    const data = await res.json()
    conversions.value = data.data || []
  } catch {}
}

onMounted(fetchConversions)
</script>

<style scoped>
.file-tools-page { max-width: 900px; margin: 0 auto; padding: 24px; }
.page-title { font-size: 1.5em; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.page-desc { color: var(--text-secondary); font-size: 0.9em; margin-bottom: 24px; }
.conv-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; margin-bottom: 24px; }
.conv-card { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-md); padding: 16px 8px; text-align: center; cursor: pointer; transition: all 0.2s; }
.conv-card:hover { border-color: #409EFF; transform: translateY(-1px); }
.conv-card.active { border-color: #409EFF; background: #f0f7ff; box-shadow: 0 0 0 1px #409EFF; }
.conv-icon { font-size: 1.6em; margin-bottom: 6px; }
.conv-name { font-size: 0.78em; color: var(--text-primary); font-weight: 500; }
.conv-panel { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg); overflow: hidden; }
.panel-header { padding: 20px 24px; border-bottom: 1px solid var(--border-default); }
.panel-title { font-size: 1.05em; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.panel-desc { font-size: 0.82em; color: var(--text-secondary); }
.panel-body { padding: 20px 24px; }
.upload-area { border: 2px dashed var(--border-default); border-radius: var(--radius-md); padding: 40px; text-align: center; cursor: pointer; transition: all 0.2s; margin-bottom: 16px; }
.upload-area:hover { border-color: #409EFF; background: #f8fbff; }
.upload-icon { font-size: 2.5em; margin-bottom: 8px; }
.upload-text { font-size: 0.95em; color: var(--text-primary); font-weight: 500; margin-bottom: 4px; }
.upload-hint { font-size: 0.78em; color: var(--text-tertiary); }
.file-list { margin-bottom: 16px; }
.file-item { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: var(--bg-subtle); border-radius: var(--radius-sm); margin-bottom: 6px; }
.file-item-name { flex: 1; font-size: 0.85em; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-item-size { font-size: 0.78em; color: var(--text-tertiary); white-space: nowrap; }
.btn-icon { width: 24px; height: 24px; border: none; background: transparent; border-radius: 50%; cursor: pointer; font-size: 0.8em; color: var(--text-tertiary); display: flex; align-items: center; justify-content: center; }
.btn-icon:hover { background: #fee2e2; color: #ef4444; }
.extra-option { margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }
.extra-option label { font-size: 0.82em; color: var(--text-secondary); white-space: nowrap; }
.input-field { flex: 1; padding: 8px 12px; border: 1px solid var(--border-default); border-radius: var(--radius-sm); font-size: 0.85em; background: var(--bg-input); color: var(--text-primary); }
.btn-convert { width: 100%; padding: 12px; border: none; border-radius: var(--radius-sm); font-size: 0.95em; font-weight: 600; background: linear-gradient(135deg, #409EFF, #337ecc); color: #fff; cursor: pointer; transition: all 0.2s; }
.btn-convert:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-convert:disabled { opacity: 0.5; cursor: default; transform: none; }
.result-bar { margin: 0 24px 20px; padding: 12px 16px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 0.85em; }
.result-bar.success { background: #f0f9f0; color: #67c23a; border: 1px solid #e1f3d8; }
.result-bar.error { background: #fef0f0; color: #f56c6c; border: 1px solid #fde2e2; }
.btn-download { padding: 6px 14px; background: #67c23a; color: #fff; border-radius: var(--radius-sm); text-decoration: none; font-size: 0.82em; font-weight: 500; }
.btn-sm { padding: 4px 12px; background: #409EFF; color: #fff; border-radius: var(--radius-sm); text-decoration: none; font-size: 0.78em; }
.history-section { padding: 20px 24px; border-top: 1px solid var(--border-default); }
.section-title { font-size: 0.95em; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }
.history-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-default); gap: 10px; }
.history-item:last-child { border-bottom: none; }
.history-info { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; flex: 1; }
.history-type { font-size: 0.78em; padding: 2px 8px; border-radius: 10px; background: #f0f7ff; color: #409EFF; font-weight: 500; }
.history-file { font-size: 0.82em; color: var(--text-primary); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-status { font-size: 0.78em; color: var(--text-secondary); white-space: nowrap; }
.history-status.completed { color: #67c23a; }
.history-status.failed { color: #f56c6c; }
</style>
