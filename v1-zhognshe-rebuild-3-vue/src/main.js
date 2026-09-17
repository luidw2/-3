/**
 * main.js —— Vue 前端应用入口文件（程序启动的“总入口”）
 * ====================================================================
 * 职责：
 *   1. 导入根组件 App.vue，创建 Vue3 应用实例；
 *   2. 注册三个全局插件：
 *      - ant-design-vue：UI 组件库（整体引入，页面模板可直接使用 a-xxx 组件）；
 *      - router：Vue Router 路由（负责页面跳转，内含登录/角色路由守卫）；
 *      - pinia：Vue3 官方状态管理（保存登录用户等全局共享数据）；
 *   3. 引入样式：antd 自带 reset 样式 + 项目自定义全局样式 style.css；
 *   4. 把整个应用挂载到 index.html 中的 <div id="app"> 节点上。
 * 架构背景：本项目为“Vue3 前端 + Flask 后端”的前后端分离课程设计，
 *           axios 请求封装（后端地址 http://127.0.0.1:5000、token 拦截器等）
 *           见 src/request.js。
 */
import { createApp } from 'vue'
import App from './App.vue'
// —— UI 组件库 ant-design-vue：全量注册，页面里可直接使用 a-xxx 组件 ——
import Antd from 'ant-design-vue';
// —— antd 组件自带的基础样式（reset），统一组件初始外观 ——
import 'ant-design-vue/dist/reset.css';
// —— 项目自定义的全局样式（CSS 变量、标签基础样式等，见 style.css）——
import './style.css';
// —— Vue Router 路由实例：页面路由表 + 全局前置守卫 ——
import router from './router';
// —— Pinia 状态管理库 ——
import { createPinia } from 'pinia'
// 创建 Pinia 实例（登录用户等全局状态都挂在这个仓库实例上）
const pinia = createPinia()

// 创建 Vue 应用 → 依次安装 Antd / 路由 / Pinia → 挂载到 #app 容器
createApp(App).use(Antd).use(router).use(pinia).mount('#app')
