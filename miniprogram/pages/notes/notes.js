const api = require("../../utils/api")
const { showError, formatTime } = require("../../utils/util")

Page({
  data: {
    notes: [],
    editing: false,
    saving: false,
    form: { id: null, title: "", content: "" },
    loading: false
  },
  onShow() {
    this.loadNotes()
  },
  async loadNotes() {
    this.setData({ loading: true })
    try {
      const notes = await api.request("/api/notes/")
      this.setData({
        notes: notes.map((item) => ({
          ...item,
          updated_at_text: formatTime(item.updated_at)
        }))
      })
    } catch (err) {
      showError(err)
    } finally {
      this.setData({ loading: false })
    }
  },
  newNote() {
    this.setData({ editing: true, form: { id: null, title: "", content: "" } })
  },
  editNote(e) {
    const id = e.currentTarget.dataset.id
    const note = this.data.notes.find((item) => item.id === id)
    if (note) this.setData({ editing: true, form: { id: note.id, title: note.title, content: note.content } })
  },
  cancelEdit() {
    this.setData({ editing: false })
  },
  onTitle(e) {
    this.setData({ "form.title": e.detail.value })
  },
  onContent(e) {
    this.setData({ "form.content": e.detail.value })
  },
  async saveNote() {
    this.setData({ saving: true })
    const form = this.data.form
    try {
      if (form.id) {
        await api.request(`/api/notes/${form.id}/`, { method: "PUT", data: form })
      } else {
        await api.request("/api/notes/", { method: "POST", data: form })
      }
      this.setData({ editing: false })
      await this.loadNotes()
    } catch (err) {
      showError(err)
    } finally {
      this.setData({ saving: false })
    }
  },
  async deleteNote(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: "删除笔记",
      content: "确定删除这条笔记吗？",
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.request(`/api/notes/${id}/`, { method: "DELETE" })
          await this.loadNotes()
        } catch (err) {
          showError(err)
        }
      }
    })
  }
})
