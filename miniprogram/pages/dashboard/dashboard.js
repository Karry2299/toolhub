const api = require("../../utils/api")
const { showError, formatTime } = require("../../utils/util")

Page({
  data: {
    stats: [],
    recentNotes: [],
    upcomingReminders: []
  },
  onShow() {
    this.load()
  },
  async load() {
    try {
      const data = await api.request("/api/dashboard/summary/")
      const counts = data.counts || {}
      this.setData({
        stats: [
          { label: "笔记", value: counts.notes || 0 },
          { label: "待办", value: counts.todos_open || 0 },
          { label: "文件", value: counts.files || 0 },
          { label: "本月账本", value: data.expense_month_total || "0" }
        ],
        recentNotes: data.recent_notes || [],
        upcomingReminders: (data.upcoming_reminders || []).map((item) => ({
          ...item,
          remind_at: formatTime(item.remind_at)
        }))
      })
    } catch (err) {
      showError(err)
    }
  }
})
