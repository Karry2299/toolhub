function showError(err) {
  wx.showToast({
    title: err && err.message ? err.message : "操作失败",
    icon: "none"
  })
}

function formatTime(value) {
  if (!value) return ""
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n) => String(n).padStart(2, "0")
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function randomPassword(options) {
  const upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  const lower = "abcdefghijklmnopqrstuvwxyz"
  const digits = "0123456789"
  const symbols = "!@#$%^&*()_+-={}[]:;,.?"
  let pool = ""
  if (options.upper) pool += upper
  if (options.lower) pool += lower
  if (options.digits) pool += digits
  if (options.symbols) pool += symbols
  if (!pool) return ""
  let result = ""
  for (let i = 0; i < options.length; i += 1) {
    result += pool[Math.floor(Math.random() * pool.length)]
  }
  return result
}

module.exports = {
  showError,
  formatTime,
  randomPassword
}
