<template><div class="qr-gen">
<h2 class="section-title">📱 二维码生成</h2>
<div class="qr-form">
<textarea v-model="text" placeholder="输入链接或文本..." rows="4" class="qr-input"></textarea>
<div class="qr-options">
<label>大小: <select v-model.number="size"><option :value="150">150x150</option><option :value="200">200x200</option><option :value="300">300x300</option><option :value="400">400x400</option></select></label>
</div>
<button @click="generate" class="btn-primary">📱 生成二维码</button>
</div>
<div v-if="qrUrl" class="qr-result">
<img :src="qrUrl" alt="QR Code" />
<a :href="qrUrl" download="qrcode.png" class="btn-download">下载</a>
</div>
</div></template>
<script setup>
import { ref } from "vue"
const text = ref("https://github.com")
const size = ref(200)
const qrUrl = ref("")
function generate() {
  if (!text.value.trim()) return
  qrUrl.value = "/api/qrcode/?text=" + encodeURIComponent(text.value) + "&size=" + size.value
}
generate()
</script>
<style scoped>
.qr-gen { max-width: 500px; margin: 0 auto; text-align: center; }
.qr-form { display: flex; flex-direction: column; gap: 15px; }
.qr-input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; resize: vertical; font-size: 1em; }
.qr-options label { display: flex; align-items: center; gap: 8px; justify-content: center; }
.qr-options select { padding: 6px 12px; border: 1px solid #ddd; border-radius: 6px; }
.qr-result { margin-top: 20px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.qr-result img { border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: #fff; }
.btn-download { background: #27ae60; color: #fff; border: none; padding: 8px 24px; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; }
</style>