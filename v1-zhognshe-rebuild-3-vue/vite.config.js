/**
 * Vite 配置文件 —— 前端（Vue3）开发服务器
 *
 * 【同源方案】开发期由 Vite 自己把接口请求转发给后端，从根上避免跨域：
 *   - 浏览器只访问一个地址（页面 + 接口同源），CORS 完全不参与；
 *   - server.proxy 把 /user、/api、/product 等接口前缀转发到 http://127.0.0.1:5000；
 *   - 前端 src/request.js 的 API_BASE_URL 默认留空（相对路径），配合本代理工作。
 *   这样前端代码里不再出现任何硬编码的后端地址，换环境不用改代码。
 *
 * ⚠️ 本项目页面路由与接口路径重名（例如页面 /user/login 与接口 POST /user/login、
 *    页面 /user/profile 与接口 GET /user/profile），所以代理必须区分"导航请求"和
 *    "接口请求"：浏览器的页面导航返回 index.html，只有 fetch/axios 请求才转发给后端。
 *    判断依据见下方 isPageNavigation()。若将来把后端接口统一收到 /api/** 前缀下，
 *    这个 bypass 就可以去掉了。
 *
 * 对外监听地址由环境变量控制，默认只在回环地址（安全）：
 *   host: process.env.VITE_DEV_HOST ?? '127.0.0.1'
 *   需要让虚拟机/局域网访问时（例如 Kali 做 DAST 测试），只绑那一块网卡：
 *     PowerShell:  $env:VITE_DEV_HOST='192.168.133.1'; npm run dev
 *   ⚠️ 不要写成 '0.0.0.0'：那会在校园网/公网网卡上也监听，
 *      而 dev server 提供的是未打包的源码（含接口路径与调试信息），不应对外暴露。
 *
 * 后端地址可用 VITE_BACKEND_ORIGIN 覆盖（默认 http://127.0.0.1:5000）。
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// 后端真实地址：只在 Vite 服务端使用，浏览器永远看不到它
const BACKEND = process.env.VITE_BACKEND_ORIGIN ?? 'http://127.0.0.1:5000'

// 需要转发到后端的接口前缀（与后端蓝图注册的接口路径一一对应）
const API_PREFIXES = ['/user', '/api', '/product', '/seller', '/profile', '/account', '/pay', '/static']

/**
 * 判断这是不是"浏览器在打开一个页面"（而不是前端代码在调接口）。
 * 页面导航：Accept 里有 text/html，或 Sec-Fetch-Mode: navigate。
 * 这类请求必须交给前端页面（index.html），否则会被当成接口转发给后端而返回 405。
 */
const isPageNavigation = (req) =>
  (req.headers.accept ?? '').includes('text/html') || req.headers['sec-fetch-mode'] === 'navigate'

// 生成代理配置：导航请求返回 index.html（前端路由接住），其余转发给后端
const apiProxy = {
  target: BACKEND,
  bypass: (req) => (isPageNavigation(req) ? '/index.html' : undefined)
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // '@' 快捷指向 src 目录，组件内可用 import xxx from '@/api/...' 方式引用
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // 默认只监听本机回环地址；需要外部访问时用 VITE_DEV_HOST 指定具体网卡
    host: process.env.VITE_DEV_HOST ?? '127.0.0.1',
    // 前端端口
    port: 5173,
    // 开发期同源代理：浏览器请求的是 5173，由 Vite 在服务端转发给后端 5000
    proxy: Object.fromEntries(API_PREFIXES.map((prefix) => [prefix, apiProxy]))
    // 未配置 hmr，本地开发默认开启热更新(HMR)：修改代码后页面即时生效
  }
})
