/**
 * Vite 配置文件 —— 前端（Vue3）开发服务器
 *
 * 本地开发方案（127.0.0.1，无 cpolar 内网穿透）：
 *   - 开发服务器只监听本机 127.0.0.1:5173；
 *   - 接口请求跨域直连后端 http://127.0.0.1:5000（后端地址见 src/request.js 的 API_BASE_URL）；
 *   - 因此后端 config/config.py 的 CORS 白名单需放行 http://127.0.0.1:5173（已配置）。
 *
 * 注意：不要为了"让手机/外网访问"而随意改回 host: '0.0.0.0'，
 * 需要外网访问时请使用 cpolar 等隧道工具把 5173 端口映射出去即可。
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // '@' 快捷指向 src 目录，组件内可用 import xxx from '@/api/...' 方式引用
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // 只监听本机回环地址：仅本机可通过 http://127.0.0.1:5173 访问页面
    host: '127.0.0.1',
    // 前端端口；与后端 config.py 中 CORS_ORIGINS 白名单里的 5173 保持一致
    port: 5173,
    // 未配置 hmr，本地开发默认开启热更新(HMR)：修改代码后页面即时生效
  }
})
