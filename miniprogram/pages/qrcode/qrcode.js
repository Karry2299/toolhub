const api = require("../../utils/api")
const { API_BASE_URL } = require("../../utils/config")
const { showError, formatTime } = require("../../utils/util")

Page({
  data: { text: "", qrUrl: "", records: [] },
  onShow() { this.loadRecords() },
  onText(e) { this.setData({ text: e.detail.value }) },
  async generate() {
    const text = this.data.text.trim()
    if (!text) { wx.showToast({ title: "请输入内容", icon: "none" }); return }
    this.setData({ qrUrl: `${API_BASE_URL}/api/qrcode/?text=${encodeURIComponent(text)}&size=260` })
    try {
      await api.request("/api/qrcodes/", { method: "POST", data: { content: text, size: 260 } })
      await this.loadRecords()
    } catch (err) { showError(err) }
  },
  async loadRecords() {
    try {
      const records = await api.request("/api/qrcodes/")
      this.setData({ records: records.map((item) => ({ ...item, created_at_text: formatTime(item.created_at) })) })
    } catch (err) { showError(err) }
  }
})
