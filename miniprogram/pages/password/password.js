const api = require("../../utils/api")
const { showError, randomPassword, formatTime } = require("../../utils/util")

Page({
  data: { password: "", length: 16, upper: true, lower: true, digits: true, symbols: true, note: "", saved: [] },
  onShow() { this.generate(); this.loadSaved() },
  onLength(e) { this.setData({ length: e.detail.value }) },
  onNote(e) { this.setData({ note: e.detail.value }) },
  toggleOption(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ [key]: !this.data[key] })
  },
  generate() {
    const password = randomPassword(this.data)
    if (!password) { wx.showToast({ title: "至少选择一种字符", icon: "none" }); return }
    this.setData({ password })
  },
  copyPassword() { if (this.data.password) wx.setClipboardData({ data: this.data.password }) },
  copySaved(e) { wx.setClipboardData({ data: e.currentTarget.dataset.value }) },
  async savePassword() {
    if (!this.data.password) return
    try {
      await api.request("/api/passwords/", {
        method: "POST",
        data: {
          password: this.data.password,
          length: this.data.length,
          has_upper: this.data.upper,
          has_lower: this.data.lower,
          has_digits: this.data.digits,
          has_symbols: this.data.symbols,
          note: this.data.note
        }
      })
      this.setData({ note: "" })
      await this.loadSaved()
      wx.showToast({ title: "已保存" })
    } catch (err) { showError(err) }
  },
  async loadSaved() {
    try {
      const saved = await api.request("/api/passwords/")
      this.setData({ saved: saved.map((item) => ({ ...item, created_at_text: formatTime(item.created_at) })) })
    } catch (err) { showError(err) }
  }
})
