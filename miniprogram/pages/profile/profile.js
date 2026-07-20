const { API_BASE_URL } = require("../../utils/config")

Page({
  data: { user: {}, initial: "T", apiBaseUrl: API_BASE_URL },
  onShow() {
    const user = wx.getStorageSync("toolhub_user") || {}
    this.setData({
      user,
      initial: user.username ? user.username.slice(0, 1).toUpperCase() : "T"
    })
  },
  logout() {
    wx.removeStorageSync("toolhub_token")
    wx.removeStorageSync("toolhub_user")
    wx.reLaunch({ url: "/pages/login/login" })
  }
})
