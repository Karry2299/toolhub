Page({
  data: {
    user: {},
    tools: [
      { name: "仪表盘", desc: "汇总数据", icon: "▦", url: "/pages/dashboard/dashboard" },
      { name: "笔记", desc: "记录想法", icon: "✎", url: "/pages/notes/notes" },
      { name: "待办", desc: "任务清单", icon: "✓", url: "/pages/todos/todos" },
      { name: "密码", desc: "生成密码", icon: "⌘", url: "/pages/password/password" },
      { name: "二维码", desc: "文本转码", icon: "▣", url: "/pages/qrcode/qrcode" },
      { name: "我的", desc: "账号设置", icon: "☻", url: "/pages/profile/profile", tab: true }
    ]
  },
  onShow() {
    const token = wx.getStorageSync("toolhub_token")
    if (!token) {
      wx.reLaunch({ url: "/pages/login/login" })
      return
    }
    this.setData({ user: wx.getStorageSync("toolhub_user") || {} })
  },
  openTool(e) {
    const url = e.currentTarget.dataset.url
    if (url === "/pages/profile/profile") {
      wx.switchTab({ url })
    } else {
      wx.navigateTo({ url })
    }
  }
})
