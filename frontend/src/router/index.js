import { createRouter, createWebHistory } from "vue-router"
import { auth } from "../auth.js"
import Home from "../views/Home.vue"

const routes = [
  { path: "/", name: "Home", component: Home, meta: { title: "首页" } },
  { path: "/dashboard", name: "Dashboard", component: () => import("../views/Dashboard.vue"), meta: { title: "个人仪表盘" } },
  { path: "/notes", name: "Notes", component: () => import("../views/Notes.vue"), meta: { title: "在线笔记" } },
  { path: "/todo", name: "Todo", component: () => import("../views/Todo.vue"), meta: { title: "待办事项" } },
  { path: "/productivity", name: "Productivity", component: () => import("../views/Productivity.vue"), meta: { title: "效率工具" } },
  { path: "/utility-tools", name: "UtilityTools", component: () => import("../views/UtilityTools.vue"), meta: { title: "文本与图片工具" } },
  { path: "/image-organizer", name: "ImageOrganizer", component: () => import("../views/ImageOrganizer.vue"), meta: { title: "图片整理" } },
  { path: "/password", name: "Password", component: () => import("../views/PasswordGenerator.vue"), meta: { title: "密码生成器" } },
  { path: "/qrcode", name: "QRCode", component: () => import("../views/QrGenerator.vue"), meta: { title: "二维码生成" } },
  { path: "/ip-lookup", name: "IpLookup", component: () => import("../views/IpLookup.vue"), meta: { title: "IP/域名查询" } },
  { path: "/files", name: "FileManager", component: () => import("../views/FileManager.vue"), meta: { title: "文件管理" } },
  { path: "/file-tools", name: "FileTools", component: () => import("../views/FileTools.vue"), meta: { title: "文档处理" } },
  { path: "/login", name: "Login", component: () => import("../views/Login.vue"), meta: { title: "登录", guest: true } },
  { path: "/register", name: "Register", component: () => import("../views/Register.vue"), meta: { title: "注册", guest: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = (to.meta?.title ? to.meta.title + " - " : "") + "ToolHub"
  if (to.meta?.guest || auth.isLoggedIn) {
    next()
  } else {
    next("/login")
  }
})

export default router
