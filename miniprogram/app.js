const { API_BASE_URL } = require("./utils/config")

App({
  globalData: {
    apiBaseUrl: API_BASE_URL,
    token: "",
    user: null
  },
  onLaunch() {
    this.globalData.token = wx.getStorageSync("toolhub_token") || ""
    this.globalData.user = wx.getStorageSync("toolhub_user") || null
  }
})
