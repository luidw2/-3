<template>
  <!-- ============================================================
       App.vue —— Vue 应用根组件（页面外壳的“分流层”）
       根据当前路由地址选择要渲染的“页面外壳”：
       - /user/login、/user/register、/user/certLogin：登录 / 注册 /
         证书登录三个页面需要整页展示（不带公共导航栏）；
       - 其余所有业务页面：统一交给 BasicLayout 公共布局渲染，
         由 BasicLayout 内部的 <router-view> 按路由动态挂载子页面。
       同时本组件监听路由变化：只要已登录（本地有 token）且进入的是
       业务页面，就自动向后端拉取并同步当前登录用户信息。
       ============================================================ -->
  <div>
    <!-- 登录和注册页面不使用 BasicLayout -->
    <UserLoginPage v-if="$route.path === '/user/login'" />
    <UserRegisterPage v-else-if="$route.path === '/user/register'" />
    <UserCertLoginPage v-else-if="$route.path === '/user/certLogin'" />
    <!-- 后台登录页同样整页展示（不带商城公共导航） -->
    <StaffLoginPage v-else-if="$route.path === '/staff/login'" />
    <TotpBindPage v-else-if="$route.path === '/staff/totp/setup'" />
    <!-- 其他页面使用 BasicLayout -->
    <BasicLayout v-else />
  </div>
</template>

<style></style>
<script setup lang="ts">
/**
 * [文件级说明] App.vue —— Vue 应用根组件
 * ------------------------------------------------------------------
 * 职责：
 *   1. 根组件本身不承载具体业务，只做“页面外壳分发”：
 *      登录类页面整页渲染，其它页面统一套用 BasicLayout；
 *   2. 监听路由变化并同步登录状态：已登录用户进入业务页面时，
 *      调用 Pinia Store 的 fetchLoginUser() 向后端拉取用户信息。
 * 说明：登录用户全局状态由 Pinia 管理（useLoginUserStore，
 *       见 src/store/useLoginUserStore.js），token 存于 localStorage。
 */
import BasicLayout from "@/layout/BasicLayout.vue";
import UserLoginPage from "@/pages/user/UserLoginPage.vue";
import UserRegisterPage from "@/pages/user/UserRegisterPage.vue";
import UserCertLoginPage from "@/pages/user/UserCertLoginPage.vue";
// 后台账号登录页（整页展示，区别于前台商城登录）
import StaffLoginPage from "@/pages/staff/StaffLoginPage.vue";
// 登录用户全局状态 Store（跨组件共享用户名 / 角色等信息）
import { useLoginUserStore } from "@/store/useLoginUserStore";
import TotpBindPage from "@/pages/staff/TotpBindPage.vue";
// 当前路由对象（配合 watch 监听路由变化）
import { useRoute } from "vue-router";

// 获取登录用户 Store 实例（供下方拉取用户信息使用）
const loginUserStore = useLoginUserStore();
// 获取当前路由对象
const route = useRoute();

// 只在非登录/注册页面获取用户信息
import { watch } from "vue";

// 监听路由 path 变化（immediate: true → 组件创建后立即执行一次）：
// 当本地存有 token（说明已登录）且目标不是登录/注册/证书登录页、也不是
// 后台页面（/staff /admin /auditor，后台账号用 /api/staff/me 恢复登录态）时，
// 调用 fetchLoginUser() 向后端拉取最新用户信息，保持全局登录态同步。
watch(() => route.path, (newPath) => {
  const hasToken = Boolean(localStorage.getItem('token'));
  const isStaffPath = ['/staff', '/admin', '/auditor'].some(p => newPath.startsWith(p));
  if (hasToken && !isStaffPath && newPath !== '/user/login' && newPath !== '/user/register' && newPath !== '/user/certLogin') {
    loginUserStore.fetchLoginUser();
  }
}, { immediate: true });

</script>
