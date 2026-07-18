<template>
  <div class="utility-page">
    <h1 class="section-title">Utility Tools</h1>
    <div class="utility-grid">
      <section class="panel card">
        <h2>Text Tools</h2>
        <textarea v-model="textInput" class="input text-area" rows="8" placeholder="Input text, JSON, URL, or Base64"></textarea>
        <div class="button-grid">
          <button class="btn btn-ghost" @click="formatJson">Format JSON</button>
          <button class="btn btn-ghost" @click="encodeUrl">URL Encode</button>
          <button class="btn btn-ghost" @click="decodeUrl">URL Decode</button>
          <button class="btn btn-ghost" @click="encodeBase64">Base64 Encode</button>
          <button class="btn btn-ghost" @click="decodeBase64">Base64 Decode</button>
          <button class="btn btn-ghost" @click="toUpper">Uppercase</button>
          <button class="btn btn-ghost" @click="toLower">Lowercase</button>
          <button class="btn btn-ghost" @click="copyText">Copy Result</button>
        </div>
        <div class="text-stats">Chars {{ textInput.length }} · Lines {{ lineCount }} · Words {{ wordCount }}</div>
        <textarea v-model="textOutput" class="input text-area output" rows="8" placeholder="Result"></textarea>
      </section>

      <section class="panel card">
        <h2>Image Size Compressor</h2>
        <input type="file" accept="image/*" class="input" @change="selectImage" />
        <div class="image-options">
          <label>Mode
            <select v-model="imageForm.operation" class="input">
              <option value="target">Under target size</option>
              <option value="compress">Fixed quality convert</option>
              <option value="resize">Resize</option>
              <option value="base64">To Base64</option>
            </select>
          </label>
          <label>Target KB
            <input v-model.number="imageForm.target_kb" class="input" type="number" min="20" />
          </label>
          <label>Format
            <select v-model="imageForm.format" class="input">
              <option value="WEBP">WEBP</option>
              <option value="JPEG">JPEG</option>
              <option value="PNG">PNG</option>
            </select>
          </label>
          <label>Quality
            <input v-model.number="imageForm.quality" class="input" type="number" min="10" max="95" />
          </label>
          <label>Width
            <input v-model.number="imageForm.width" class="input" type="number" min="1" placeholder="Optional" />
          </label>
          <label>Height
            <input v-model.number="imageForm.height" class="input" type="number" min="1" placeholder="Optional" />
          </label>
        </div>
        <button class="btn btn-accent" :disabled="!imageFile || imageLoading" @click="processImage">
          {{ imageLoading ? "Processing..." : "Process Image" }}
        </button>
        <router-link to="/image-organizer" class="organizer-link">Batch organize images</router-link>
        <p class="hint">Target mode keeps dimensions first and only reduces quality/size as needed to fit the limit.</p>
        <p v-if="imageError" class="error">{{ imageError }}</p>
        <div v-if="imageResult.download_url" class="result-box">
          <a class="btn btn-success" :href="imageResult.download_url" download>Download Result</a>
          <span v-if="imageResult.final_size" class="result-meta">
            {{ formatBytes(imageResult.final_size) }} · {{ imageResult.final_width }}x{{ imageResult.final_height }}
          </span>
        </div>
        <textarea v-if="imageResult.result_text" v-model="imageResult.result_text" class="input text-area output" rows="8"></textarea>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { auth, authUploadHeaders } from "../auth.js"

const textInput = ref("")
const textOutput = ref("")
const imageFile = ref(null)
const imageLoading = ref(false)
const imageError = ref("")
const imageResult = ref({})
const imageForm = ref({ operation: "target", target_kb: 1024, format: "WEBP", quality: 90, width: "", height: "" })

const lineCount = computed(() => textInput.value ? textInput.value.split(/\r?\n/).length : 0)
const wordCount = computed(() => textInput.value.trim() ? textInput.value.trim().split(/\s+/).length : 0)

function setOutput(value, action) {
  textOutput.value = value
  fetch("/api/text-tools/log/", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Token " + auth.token },
    body: JSON.stringify({ action, detail: textInput.value.slice(0, 120) }),
  }).catch(() => {})
}

function formatJson() {
  try { setOutput(JSON.stringify(JSON.parse(textInput.value), null, 2), "json-format") }
  catch (e) { setOutput("JSON error: " + e.message, "json-format-failed") }
}
function encodeUrl() { setOutput(encodeURIComponent(textInput.value), "url-encode") }
function decodeUrl() { setOutput(decodeURIComponent(textInput.value), "url-decode") }
function encodeBase64() { setOutput(btoa(unescape(encodeURIComponent(textInput.value))), "base64-encode") }
function decodeBase64() {
  try { setOutput(decodeURIComponent(escape(atob(textInput.value))), "base64-decode") }
  catch (e) { setOutput("Base64 decode failed", "base64-decode-failed") }
}
function toUpper() { setOutput(textInput.value.toUpperCase(), "upper") }
function toLower() { setOutput(textInput.value.toLowerCase(), "lower") }
function copyText() { navigator.clipboard.writeText(textOutput.value || textInput.value) }

function selectImage(e) {
  imageFile.value = e.target.files[0] || null
  imageResult.value = {}
  imageError.value = ""
}

function formatBytes(bytes) {
  if (!bytes) return "0 B"
  if (bytes < 1024) return bytes + " B"
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
  return (bytes / 1024 / 1024).toFixed(2) + " MB"
}

async function processImage() {
  if (!imageFile.value) return
  imageLoading.value = true
  imageError.value = ""
  imageResult.value = {}
  const form = new FormData()
  form.append("file", imageFile.value)
  for (const [key, value] of Object.entries(imageForm.value)) {
    if (value !== "" && value !== null) form.append(key, value)
  }
  try {
    const r = await fetch("/api/image-tools/process/", { method: "POST", headers: authUploadHeaders(), body: form })
    const data = await r.json()
    if (!r.ok || !data.success) {
      imageError.value = data.error || "Image processing failed"
      return
    }
    imageResult.value = data.data || { result_text: data.result_text }
  } catch (e) {
    imageError.value = "Request failed: " + e.message
  } finally {
    imageLoading.value = false
  }
}
</script>

<style scoped>
.utility-page { max-width: var(--max-width); margin: 0 auto; }
.utility-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; align-items: start; }
.panel { padding: 20px; }
.panel h2 { font-size: 1.05em; margin-bottom: 12px; }
.text-area { width: 100%; resize: vertical; font-family: "SF Mono", Consolas, monospace; margin-bottom: 12px; }
.output { background: #f8fafc; }
.button-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-bottom: 12px; }
.button-grid .btn { justify-content: center; padding: 8px 10px; }
.text-stats, .hint, .result-meta { color: var(--text-secondary); font-size: 0.86em; margin: 10px 0; }
.image-options { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 12px 0; }
.image-options label { display: flex; flex-direction: column; gap: 5px; color: var(--text-secondary); font-size: 0.86em; }
.result-box { margin-top: 14px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.error { color: var(--bg-danger); margin-top: 10px; }
.organizer-link { display: inline-flex; margin-left: 10px; color: var(--text-accent); font-size: 0.9em; }
</style>
