<template><div class="todo">
<h2 class="section-title">✅ 待办事项</h2>
<div class="todo-input-row">
<input v-model="newTodo" @keyup.enter="addTodo" placeholder="输入新任务..." class="todo-input" />
<button @click="addTodo" class="btn-primary">添加</button>
</div>
<div class="todo-filters">
<button v-for="f in filters" :key="f.key" @click="activeFilter=f.key" :class="activeFilter === f.key ? 'filter-btn active' : 'filter-btn'">{{ f.label }}</button>
</div>
<div class="todo-list">
<div v-for="item in filteredTodos" :key="item.id" class="todo-item" :class="{done: item.completed}">
<input type="checkbox" v-model="item.completed" @change="toggleTodo(item)" />
<span class="todo-text" @dblclick="editTodo(item)">{{ item.title }}</span>
<button @click="deleteTodo(item.id)" class="btn-icon">✖</button>
</div>
<div v-if="filteredTodos.length === 0" class="todo-empty">暂无任务</div>
</div>
<div class="todo-stats">{{ todos.filter(t=>!t.completed).length }}项待办 / 共{{ todos.length }}项</div>
</div></template>
<script setup>
import { ref, computed, onMounted } from "vue"
import { authHeaders } from "../auth.js"
const todos = ref([]); const newTodo = ref(""); const activeFilter = ref("all")
const API = "/api/todos/"
const filters = [{key:"all",label:"全部"},{key:"active",label:"待办"},{key:"done",label:"已完成"}]
const filteredTodos = computed(() => {
  if (activeFilter.value === "active") return todos.value.filter(t => !t.completed)
  if (activeFilter.value === "done") return todos.value.filter(t => t.completed)
  return todos.value
})
async function fetchTodos() {
  try { const r = await fetch(API, { headers: authHeaders() }); todos.value = await r.json() }
  catch(e) { console.error(e) }
}
async function addTodo() {
  if (!newTodo.value.trim()) return
  try {
    const r = await fetch(API, { method: "POST", headers: authHeaders(), body: JSON.stringify({title: newTodo.value}) })
    todos.value.push(await r.json()); newTodo.value = ""
  } catch(e) { console.error(e) }
}
async function toggleTodo(item) {
  try { await fetch(API + item.id + "/", { method: "PATCH", headers: authHeaders(), body: JSON.stringify({completed: item.completed}) }) }
  catch(e) { console.error(e) }
}
async function deleteTodo(id) {
  try { await fetch(API + id + "/", { method: "DELETE", headers: authHeaders() }); todos.value = todos.value.filter(t => t.id !== id) }
  catch(e) { console.error(e) }
}
onMounted(fetchTodos)
</script>
<style scoped>
.todo { max-width: 600px; margin: 0 auto; }
.todo-input-row { display: flex; gap: 10px; margin-bottom: 15px; }
.todo-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 1em; }
.todo-filters { display: flex; gap: 8px; margin-bottom: 15px; }
.filter-btn { background: #ecf0f1; border: none; padding: 6px 16px; border-radius: 20px; cursor: pointer; font-size: 0.85em; }
.filter-btn.active { background: #3498db; color: #fff; }
.todo-item { display: flex; align-items: center; gap: 12px; background: #fff; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #eee; }
.todo-item.done .todo-text { text-decoration: line-through; color: #bdc3c7; }
.todo-text { flex: 1; cursor: pointer; }
.btn-icon { background: none; border: none; cursor: pointer; color: #e74c3c; font-size: 1.1em; }
.todo-empty { text-align: center; padding: 40px; color: #bdc3c7; }
.todo-stats { margin-top: 15px; color: #95a5a6; font-size: 0.9em; text-align: center; }
</style>
