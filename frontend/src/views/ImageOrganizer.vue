<template>
  <div class="image-page">
    <div class="page-head">
      <div>
        <h1 class="section-title">Image Organizer</h1>
        <p class="subtle">Upload, tag, favorite, find duplicates, and batch-compress images.</p>
      </div>
      <label class="btn btn-accent upload-btn">
        Upload Images
        <input type="file" accept="image/*" multiple hidden @change="uploadImages" />
      </label>
    </div>

    <div class="toolbar card">
      <input v-model="filters.q" class="input" placeholder="Search filename, title, or tags" @keyup.enter="loadImages" />
      <select v-model="filters.category" class="input" @change="loadImages">
        <option value="">All categories</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <label class="toggle"><input type="checkbox" v-model="filters.favorite" @change="loadImages" /> Favorites</label>
      <label class="toggle"><input type="checkbox" v-model="filters.duplicates" @change="loadImages" /> Duplicates</label>
      <button class="btn btn-ghost" @click="loadImages">Refresh</button>
    </div>

    <div class="batch card">
      <span>Selected {{ selectedIds.length }}</span>
      <select v-model="batch.format" class="input small">
        <option value="WEBP">WEBP</option>
        <option value="JPEG">JPEG</option>
        <option value="PNG">PNG</option>
      </select>
      <input v-model.number="batch.quality" class="input tiny" type="number" min="10" max="95" />
      <button class="btn btn-success" :disabled="!selectedIds.length || batchLoading" @click="batchCompress">
        {{ batchLoading ? "Working..." : "Download ZIP" }}
      </button>
      <span class="batch-hint">ZIP is for multiple images. Use per-image target download below for upload limits.</span>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading" class="state">Loading...</div>
    <div v-else-if="!images.length" class="state">No images yet. Upload a few to start organizing.</div>
    <div v-else class="image-grid">
      <article v-for="img in images" :key="img.id" class="image-card card">
        <label class="select-box"><input type="checkbox" :value="img.id" v-model="selectedIds" /></label>
        <img :src="img.image_url" :alt="img.original_filename" />
        <div class="image-body">
          <input v-model="img.title" class="inline-input title" placeholder="Title" @change="saveMeta(img)" />
          <input v-model="img.category" class="inline-input" placeholder="Category" @change="saveMeta(img)" />
          <input v-model="img.tags" class="inline-input" placeholder="Tags" @change="saveMeta(img)" />
          <div class="meta">
            {{ img.width }}x{{ img.height }} · {{ img.size_display }}
            <span v-if="img.duplicate_count" class="dup">duplicates {{ img.duplicate_count }}</span>
          </div>
        </div>
        <div class="actions">
          <button class="icon-btn" :class="{ active: img.is_favorite }" @click="toggleFavorite(img)">Star</button>
          <a class="icon-btn" :href="img.image_url" target="_blank">Open</a>
          <input v-model.number="targetKbById[img.id]" class="target-input" type="number" min="20" placeholder="KB" />
          <button class="icon-btn" @click="downloadTarget(img)">Under KB</button>
          <button class="icon-btn danger" @click="deleteImage(img)">Delete</button>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { authHeaders, authUploadHeaders } from "../auth.js"

const images = ref([])
const categories = ref([])
const selectedIds = ref([])
const loading = ref(false)
const batchLoading = ref(false)
const error = ref("")
const filters = ref({ q: "", category: "", favorite: false, duplicates: false })
const batch = ref({ format: "WEBP", quality: 80 })
const targetKbById = ref({})

function buildQuery() {
  const params = new URLSearchParams()
  if (filters.value.q) params.set("q", filters.value.q)
  if (filters.value.category) params.set("category", filters.value.category)
  if (filters.value.favorite) params.set("favorite", "1")
  if (filters.value.duplicates) params.set("duplicates", "1")
  return params.toString()
}

async function loadImages() {
  loading.value = true
  error.value = ""
  try {
    const qs = buildQuery()
    const r = await fetch("/api/image-assets/" + (qs ? "?" + qs : ""), { headers: authHeaders() })
    images.value = r.ok ? await r.json() : []
    for (const img of images.value) {
      if (!targetKbById.value[img.id]) targetKbById.value[img.id] = 1024
    }
  } catch (e) {
    error.value = "Failed to load images: " + e.message
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const r = await fetch("/api/image-assets/categories/", { headers: authHeaders() })
  if (r.ok) categories.value = (await r.json()).categories || []
}

async function uploadImages(e) {
  const files = Array.from(e.target.files || [])
  e.target.value = ""
  error.value = ""
  for (const file of files) {
    const form = new FormData()
    form.append("image", file)
    form.append("title", file.name.replace(/\.[^.]+$/, ""))
    const r = await fetch("/api/image-assets/", { method: "POST", headers: authUploadHeaders(), body: form })
    if (!r.ok) error.value = "Some images failed to upload."
  }
  await loadImages()
  await loadCategories()
}

async function saveMeta(img) {
  await fetch("/api/image-assets/" + img.id + "/", {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ title: img.title, category: img.category, tags: img.tags }),
  })
  await loadCategories()
}

async function toggleFavorite(img) {
  const r = await fetch("/api/image-assets/" + img.id + "/favorite/", { method: "POST", headers: authHeaders() })
  if (r.ok) img.is_favorite = (await r.json()).is_favorite
}

async function deleteImage(img) {
  if (!confirm("Delete this image?")) return
  await fetch("/api/image-assets/" + img.id + "/", { method: "DELETE", headers: authHeaders() })
  selectedIds.value = selectedIds.value.filter(id => id !== img.id)
  await loadImages()
}

async function batchCompress() {
  batchLoading.value = true
  error.value = ""
  try {
    const r = await fetch("/api/image-assets/batch_compress/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ ids: selectedIds.value, format: batch.value.format, quality: batch.value.quality }),
    })
    if (!r.ok) {
      error.value = "Batch compression failed."
      return
    }
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "compressed-images.zip"
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = "Batch compression failed: " + e.message
  } finally {
    batchLoading.value = false
  }
}

async function downloadTarget(img) {
  const targetKb = targetKbById.value[img.id] || 1024
  error.value = ""
  try {
    const r = await fetch("/api/image-assets/" + img.id + "/compress_to_target/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ target_kb: targetKb, format: "WEBP" }),
    })
    if (!r.ok) {
      error.value = "Target compression failed."
      return
    }
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = (img.title || img.original_filename || "image") + "_under_" + targetKb + "kb.webp"
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = "Target compression failed: " + e.message
  }
}

onMounted(async () => {
  await loadImages()
  await loadCategories()
})
</script>

<style scoped>
.image-page { max-width: var(--max-width); margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.subtle { color: var(--text-secondary); margin-top: -14px; }
.upload-btn { cursor: pointer; white-space: nowrap; }
.toolbar, .batch { padding: 12px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 14px; }
.toolbar .input { min-width: 180px; }
.toggle { display: flex; gap: 6px; align-items: center; color: var(--text-secondary); }
.small { width: 110px; }
.tiny { width: 80px; }
.state, .error { text-align: center; padding: 24px; color: var(--text-tertiary); }
.error { color: var(--bg-danger); }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.image-card { position: relative; overflow: hidden; }
.select-box { position: absolute; top: 10px; left: 10px; background: rgba(255,255,255,0.9); padding: 4px 6px; border-radius: var(--radius-sm); z-index: 2; }
.image-card img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; display: block; background: #f8fafc; }
.image-body { padding: 12px; display: grid; gap: 8px; }
.inline-input { width: 100%; border: 1px solid var(--border-default); border-radius: var(--radius-sm); padding: 7px 9px; font-size: 0.86em; }
.title { font-weight: 600; }
.meta { color: var(--text-tertiary); font-size: 0.78em; }
.dup { color: var(--bg-danger); margin-left: 6px; }
.actions { padding: 0 12px 12px; display: flex; gap: 6px; }
.icon-btn { border: 1px solid var(--border-default); border-radius: var(--radius-sm); background: var(--bg-card); color: var(--text-secondary); padding: 7px 9px; cursor: pointer; font-size: 0.82em; }
.icon-btn.active { color: var(--bg-accent); border-color: var(--bg-accent); }
.icon-btn.danger { color: var(--bg-danger); }
.target-input { width: 70px; border: 1px solid var(--border-default); border-radius: var(--radius-sm); padding: 7px 8px; font-size: 0.82em; }
.batch-hint { color: var(--text-tertiary); font-size: 0.82em; }
@media (max-width: 720px) {
  .page-head { flex-direction: column; align-items: stretch; }
}
</style>
