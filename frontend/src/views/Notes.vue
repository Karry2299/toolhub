<template>
  <div class="notes">
    <h2 class="section-title">📝 在线笔记</h2>
    <div class="notes-layout">
      <div class="notes-sidebar">
        <button class="btn-primary" @click="addNote">+ 新建笔记</button>
        <div class="note-list">
          <div v-for="note in notes" :key="note.id" class="note-item" :class="{active: currentNote && currentNote.id === note.id}" @click="selectNote(note)">
            <div class="note-item-title">{{ note.title || "无标题" }}</div>
            <div class="note-item-preview">{{ note.content?.substring(0, 30) }}{{ note.content?.length > 30 ? "..." : "" }}</div>
          </div>
        </div>
      </div>
      <div class="notes-editor" v-if="currentNote">
        <input v-model="currentNote.title" class="note-title-input" placeholder="笔记标题..." />
        <textarea v-model="currentNote.content" class="note-content-input" placeholder="开始写下想法..."></textarea>
        <div class="editor-actions">
          <button class="btn-save" @click="saveNote">💾 保存</button>
          <button class="btn-danger" @click="deleteNote">🗑️ 删除</button>
        </div>
      </div>
      <div class="notes-editor notes-empty" v-else>
        <p>点击"新建笔记"或从列表中选择一个笔记</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { authHeaders } from "../auth.js"
const notes = ref([])
const currentNote = ref(null)
const API = "/api/notes/"
async function fetchNotes() {
  try { const r = await fetch(API, { headers: authHeaders() }); notes.value = await r.json() }
  catch (e) { console.error(e) }
}
function selectNote(note) { currentNote.value = { ...note } }
function addNote() {
  const newNote = { _temp: Date.now(), title: "", content: "" }
  notes.value.unshift(newNote)
  currentNote.value = newNote
}
async function saveNote() {
  const n = currentNote.value
  try {
    if (n.id) {
      const r = await fetch(API + n.id + "/", { method: "PUT", headers: authHeaders(), body: JSON.stringify(n) })
      if (!r.ok) { console.error("Save failed:", r.status); return }
      const updated = await r.json()
      Object.assign(n, updated)
    } else {
      const r = await fetch(API, { method: "POST", headers: authHeaders(), body: JSON.stringify(n) })
      if (!r.ok) { console.error("Save failed:", r.status); return }
      const saved = await r.json()
      notes.value[0] = saved
      currentNote.value = saved
    }
  } catch (e) { console.error(e) }
}
async function deleteNote() {
  if (!currentNote.value?.id) { notes.value.shift(); currentNote.value = null; return }
  try {
    await fetch(API + currentNote.value.id + "/", { method: "DELETE", headers: authHeaders() })
    notes.value = notes.value.filter(n => n.id !== currentNote.value.id)
    currentNote.value = null
  } catch (e) { console.error(e) }
}
onMounted(fetchNotes)
</script>
<style scoped>
.section-title { font-size: 1.5em; color: #2c3e50; margin-bottom: 20px; }
.notes-layout { display: flex; gap: 20px; height: calc(100vh - 200px); }
.notes-sidebar { width: 260px; flex-shrink: 0; display: flex; flex-direction: column; gap: 10px; }
.note-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.note-item { background: #fff; padding: 12px 16px; border-radius: 8px; cursor: pointer; border: 1px solid #eee; transition: all 0.2s; }
.note-item:hover { border-color: #3498db; }
.note-item.active { border-color: #3498db; background: #ebf5fb; }
.note-item-title { font-weight: 600; margin-bottom: 4px; }
.note-item-preview { font-size: 0.8em; color: #95a5a6; }
.notes-editor { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.notes-empty { justify-content: center; align-items: center; color: #bdc3c7; }
.note-title-input { font-size: 1.3em; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-weight: 600; }
.note-content-input { flex: 1; padding: 16px; border: 1px solid #ddd; border-radius: 8px; resize: none; font-size: 1em; line-height: 1.6; }
.editor-actions { display: flex; gap: 10px; }
.btn-primary { background: #3498db; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 0.95em; }
.btn-save { background: #27ae60; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
.btn-danger { background: #e74c3c; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
</style>
