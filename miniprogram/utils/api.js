const { API_BASE_URL } = require("./config")

function getToken() {
  return wx.getStorageSync("toolhub_token") || ""
}

function buildUrl(path) {
  if (path.startsWith("http")) return path
  return API_BASE_URL + path
}

function request(path, options = {}) {
  const token = getToken()
  const header = Object.assign(
    { "Content-Type": "application/json" },
    options.header || {}
  )
  if (token) header.Authorization = "Token " + token

  return new Promise((resolve, reject) => {
    wx.request({
      url: buildUrl(path),
      method: options.method || "GET",
      data: options.data || {},
      header,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }
        if (res.statusCode === 401 || res.statusCode === 403) {
          wx.removeStorageSync("toolhub_token")
          wx.removeStorageSync("toolhub_user")
          wx.reLaunch({ url: "/pages/login/login" })
        }
        const message = (res.data && (res.data.error || res.data.detail || res.data.message)) || "请求失败"
        reject(new Error(message))
      },
      fail(err) {
        reject(new Error(err.errMsg || "网络错误"))
      }
    })
  })
}

function login(username, password) {
  return request("/api/auth/login/", {
    method: "POST",
    data: { username, password }
  })
}

function register(username, password) {
  return request("/api/auth/register/", {
    method: "POST",
    data: { username, password }
  })
}

module.exports = {
  API_BASE_URL,
  request,
  login,
  register
}
