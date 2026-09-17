<template>
  <!-- ============================================================
       BasicLayout.vue —— 业务页面的公共布局外壳
       三段式布局（ant-design-vue 的 Layout 组件）：
       - 顶部 Header：全局导航栏 GlobalHeader（Logo、菜单、用户名）；
       - 中间 Content：<router-view> 按当前路由渲染具体子页面；
       - 底部 Footer：显示课程设计小组信息。
       ============================================================ -->
  <div id="basicLayout">

    <a-layout class="full-height-layout">

      <!-- 页头：全局顶部导航栏（菜单项随登录角色动态变化） -->
      <a-layout-header class="header">
        <GlobalHeader/>
      </a-layout-header>

      <!-- 内容区：路由视图，当前路由对应的子页面渲染在此处 -->
      <a-layout-content class="content">
        <router-view/>
      </a-layout-content>

      <!-- 页脚：展示项目归属 -->
      <a-layout-footer class="footer">
        <a href="https://www.uestc.edu.cn/" target="_blank">
          by 综设第五小组
        </a>
      </a-layout-footer>

    </a-layout>
  </div>
</template>

<script setup lang="ts">
/**
 * [文件级说明] BasicLayout.vue —— 业务页面的“公共布局骨架”
 * ------------------------------------------------------------------
 * 职责：除登录 / 注册 / 证书登录之外的业务页面都嵌套在本布局中展示，
 *       内容区由 <router-view> 按当前路由动态替换，因此顶部导航栏与
 *       页脚对所有业务页面保持一致，实现“页面只需写业务内容”。
 * 布局要点：外层用 flex 纵向排列并让容器高度撑满视口（见下方样式），
 *       保证内容不满一屏时页脚也能吸附在浏览器底部。
 */
// 引入全局顶部导航组件（内含动态菜单与登录用户名展示）
import GlobalHeader from "@/components/GlobalHeader.vue";
</script>

<style scoped>
/* ===== 公共布局样式（scoped：只对本组件生效）=====
   整体高度撑满视口，内部使用 flex 纵向布局：
   页头与页脚高度固定、不可压缩，内容区弹性占满剩余空间。 */

#basicLayout {
  width: 100%;
  min-height: 100vh;
}

.full-height-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 页头：白底、左右留白、固定不压缩 */
#basicLayout .header {
  background: #fff;
  color: unset;
  padding-inline: 20px;
  flex-shrink: 0;
}

/* 内容区：浅蓝渐变背景，弹性占满剩余高度，内部再显示子页面 */
#basicLayout .content {
  flex: 1;
  padding: 30px;
  background: linear-gradient(to left, #21c6fd, #00beff);
  min-height: 0;
}

/* 页脚：淡粉背景、文字居中、高度固定 */
#basicLayout .footer {
  background-color: #ffc3c3;
  text-align: center;
  padding: 24px;
  height: 64px;
  line-height: 28px;
  flex-shrink: 0;
}
</style>
