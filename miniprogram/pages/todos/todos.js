const api = require("../../utils/api")
const { showError } = require("../../utils/util")

Page({
  data: { todos: [], visibleTodos: [], filter: "all", newTitle: "", adding: false },
  onShow() { this.loadTodos() },
  async loadTodos() {
    try {
      const todos = await api.request("/api/todos/")
      this.setData({ todos })
      this.applyFilter()
    } catch (err) { showError(err) }
  },
  applyFilter() {
    let visible = this.data.todos
    if (this.data.filter === "open") visible = visible.filter((item) => !item.completed)
    if (this.data.filter === "done") visible = visible.filter((item) => item.completed)
    this.setData({ visibleTodos: visible })
  },
  setFilter(e) { this.setData({ filter: e.currentTarget.dataset.filter }); this.applyFilter() },
  onInput(e) { this.setData({ newTitle: e.detail.value }) },
  async addTodo() {
    const title = this.data.newTitle.trim()
    if (!title) return
    this.setData({ adding: true })
    try {
      await api.request("/api/todos/", { method: "POST", data: { title } })
      this.setData({ newTitle: "" })
      await this.loadTodos()
    } catch (err) { showError(err) } finally { this.setData({ adding: false }) }
  },
  async toggleTodo(e) {
    const id = e.currentTarget.dataset.id
    const todo = this.data.todos.find((item) => item.id === id)
    if (!todo) return
    try {
      await api.request(`/api/todos/${id}/`, { method: "PATCH", data: { completed: !todo.completed } })
      await this.loadTodos()
    } catch (err) { showError(err) }
  },
  async deleteTodo(e) {
    const id = e.currentTarget.dataset.id
    try {
      await api.request(`/api/todos/${id}/`, { method: "DELETE" })
      await this.loadTodos()
    } catch (err) { showError(err) }
  }
})
