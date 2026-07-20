const api = require("../../utils/api")
const { showError } = require("../../utils/util")

Page({
  data: {
    mode: "login",
    username: "",
    password: "",
    loading: false
  },
  onLoad() {
    if (wx.getStorageSync("toolhub_token")) {
      wx.switchTab({ url: "/pages/home/home" })
    }
  },
  setLogin() {
    this.setData({ mode: "login" })
  },
  setRegister() {
    this.setData({ mode: "register" })
  },
  onUsername(e) {
    this.setData({ username: e.detail.value })
  },
  onPassword(e) {
    this.setData({ password: e.detail.value })
  },
  async submit() {
    const username = this.data.username.trim()
    const password = this.data.password
    if (!username || !password) {
      wx.showToast({ title: "请输入用户名和密码", icon: "none" })
      return
    }
    this.setData({ loading: true })
    try {
      const data = this.data.mode === "login"
        ? await api.login(username, password)
        : await api.register(username, password)
      wx.setStorageSync("toolhub_token", data.token)
      wx.setStorageSync("toolhub_user", {
        username: data.username,
        user_id: data.user_id,
        is_superuser: data.is_superuser
      })
      wx.switchTab({ url: "/pages/home/home" })
    } catch (err) {
      showError(err)
    } finally {
      this.setData({ loading: false })
    }
  }
})
