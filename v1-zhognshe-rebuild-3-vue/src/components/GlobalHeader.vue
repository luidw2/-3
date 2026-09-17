<template>
  <div id="globalHeader">
    <a-row :wrap="false">

      <!-- 左列:Logo 与系统标题 -->
      <a-col flex="200px">
        <div class="title-bar">
          <img class="logo" src="../assets/vue.svg" alt="logo"></img>
          <div class="title">什么系统我也说不上来</div>
        </div>
      </a-col>

      <!-- 中列:水平导航菜单,菜单项由登录状态与角色动态决定(见 items) -->
      <a-col flex="auto">
        <a-menu
            v-model:selectedKeys="current"
            mode="horizontal"
            :items="items"
            @click="doMenuClick"
        />
      </a-col>

      <!-- 右列:显示当前登录用户名;登录态下为下拉菜单,提供“退出登录” -->
      <a-col flex="110px">
        <a-dropdown v-if="hasToken">
          <div class="user-login-status" style="cursor:pointer">
            {{ loginUserStore.loginUser.username }}
            <DownOutlined style="font-size:10px; margin-left:2px"/>
          </div>
          <template #overlay>
            <a-menu @click="onUserMenuClick">
              <a-menu-item key="logout">退出登录</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
        <div v-else class="user-login-status">{{ loginUserStore.loginUser.username }}</div>
      </a-col>

    </a-row>
  </div>
</template>
<script lang="ts" setup>
/**
 * [文件级说明] GlobalHeader.vue —— 全局顶部导航栏组件
 * ------------------------------------------------------------------
 * 布局:整行按三列划分(ant-design-vue 的 Row/Col 栅格):
 *   1. 左列(固定宽):Logo 与系统标题;
 *   2. 中列(自适应):水平导航菜单,菜单项随“是否登录 + 用户角色”动态生成:
 *        - 未登录       :仅显示“主页”;
 *        - 卖家 seller  :基础项 + 创建商品 + 查看商品(卖家管理);
 *        - 买家 user    :基础项 + 查看商品 + 购物车 + 我的订单;
 *   3. 右列(固定宽):当前登录用户名(读取 Pinia Store,默认“未登录”);
 *      登录态下是下拉菜单,内含“退出登录”(★必须清除本地 token,否则刷新页面/
 *      从登录页“返回商城”后仍能以原身份进入后台 —— 这是前后台共同的登出入口)。
 * 交互机制:
 *   - 菜单项 key 就是路由路径,点击后 router.push 完成跳转;
 *   - 路由跳转成功后通过 router.afterEach 同步菜单高亮(current);
 *   - “退出登录”:后台账号调 /api/staff/logout、前台账号调 /user/logout 后,
 *     无论接口成败都清除 localStorage 的 token、重置 store,再跳对应登录页。
 */
import {computed, h, ref} from 'vue';
import {HomeOutlined, DownOutlined} from '@ant-design/icons-vue';
import {MenuProps, message} from 'ant-design-vue';
import {useRouter} from "vue-router";
import {userLogOut} from '@/api/user';
import {staffLogout} from '@/api/staff';

import {useLoginUserStore} from "@/store/useLoginUserStore"

// 登录用户 Store:读取 username / role 用于菜单与用户名展示
const loginUserStore = useLoginUserStore();

// 是否持有登录令牌(有 token 才显示用户名下拉,否则只显示“未登录”)
const hasToken = computed(() => Boolean(localStorage.getItem('token')));


//点击菜单跳转函数
const router = useRouter();
// 菜单项被点击时触发:key 就是对应的路由路径,直接跳转过去
const doMenuClick = ({key}: { key: string }) => {
  router.push({path: key});
}

// 用户名下拉菜单点击:目前只有“退出登录”
// 退出必须同时完成:① 通知后端注销会话(尽力而为) ② 清除本地 token
// ③ 重置 store 登录态 ④ 跳回对应登录页 —— 缺任一步都会让旧 token 残留,
// 造成“从登录页返回商城后仍能直接进入后台”的问题
const onUserMenuClick = async ({key}: { key: string }) => {
  if (key !== 'logout') {
    return;
  }
  const role = loginUserStore.loginUser?.role;
  try {
    // 后台账号(admin/auditor)调 staff 登出接口(记 STAFF_LOGOUT 审计);
    // 前台用户/商家调 /user/logout。接口需带 token,故在清理本地状态前调用
    if (role === 'admin' || role === 'auditor') {
      await staffLogout();
    } else {
      await userLogOut({});
    }
  } catch (e) {
    // 接口失败(如令牌已过期)不阻断退出:本地状态必须无条件清理
    console.warn('通知后端登出失败(将仍清理本地登录态):', e);
  } finally {
    // ★ 清除本地 token —— 这是“退出登录”的核心,必须无条件执行
    localStorage.removeItem('token');
    loginUserStore.setLoginUser({username: '未登录'});
    message.success('已退出登录');
    const target = (role === 'admin' || role === 'auditor') ? '/staff/login' : '/user/login';
    router.push({path: target, replace: true});   // replace 防止后退回到原页面
  }
};

// 当前高亮的菜单项(对应 a-menu 的 selectedKeys);初始值无实际意义,
// 每次路由跳转成功后会被覆盖为当前路径
const current = ref<string[]>(['mail']);

// 路由跳转成功后,把菜单高亮同步成当前页面的路径(跟随导航高亮)
router.afterEach((to, from, failure) => {
  current.value = [to.path];
})

// 计算属性动态生成菜单项(依赖登录状态与角色变化自动重新计算):
//   1. 未登录 → 只保留“主页”;
//   2. 卖家 seller → 基础菜单 + “创建商品 / 查看商品(卖家管理)”;
//   3. 其它已登录用户(买家 user)→ 基础菜单 + “查看商品 / 购物车 / 我的订单”。
const items = computed<MenuProps['items']>(() => {
  const baseItems = [
    {
      key: '/',
      icon: () => h(HomeOutlined),
      label: '主页',
      title: '主页',
    },
    {
      key: '/user/profile',
      label: '个人中心',
      title: '个人中心',
    },
    {
        key: '/user/login',
        label: '用户登录',
        title: '用户登录',
      },
      {
        key: '/user/register',
        label: '用户注册',
        title: '用户注册',
      },
  ];

  // 未登录:导航栏只显示“主页”(登录/注册入口在登录页上自行提供)
  if (!localStorage.getItem('token')) {
    return [
      baseItems[0],
        {
        key: '/user/login',
        label: '用户登录',
        title: '用户登录',
      },
      {
        key: '/staff/login',
        label: '后台人员登录',
        title: '后台人员登录',
      },
    ];
  }

  // 已登录:读取当前用户角色,再按角色决定追加哪些菜单
  const role = loginUserStore.loginUser?.role;
  // 管理员:后台管理菜单(账号管理/商品管理/TOTP 设置)
  if (role === 'admin') {
    return [
      baseItems[0],
      {
        label: '账号管理',
        key: '/admin/accounts',
      },
      {
        label: '商品管理',
        key: '/admin/products',
      },
    ];
  }
  // 审计员:审计中心菜单(审计日志/TOTP 设置)
  if (role === 'auditor') {
    return [
      baseItems[0],
      {
        label: '审计日志',
        key: '/auditor/logs',
      },
    ];
  }
  // 卖家角色:追加“创建商品 / 查看商品(卖家端管理)”
  if (role === 'seller') {
    return [
      ...baseItems,
          {
            label: '创建商品',
            key: '/product/create',
          },
          {
            label: '查看商品',
            key: '/seller/products/profile',
          },
    ];
  }

  // 买家等其它已登录角色:追加“查看商品 / 购物车 / 我的订单”
  return [
    ...baseItems,
        {
          label: '查看商品',
          key: '/user/products/profile',
        },
        {
          label: '购物车',
          key: '/user/shopping_cart_profile',
        },
        {
          label: '我的订单',
          key: '/user/profile_order',
        },
  ];
});
</script>

<style scoped>
/* ===== 顶部导航栏样式(左侧标题区)===== */
.title-bar {
  display: flex;
  align-items: center;
}

/* 标题文字:深色、小号、与 Logo 间距 8px */
.title {
  color: #2c3e50;
  font-size: 12px;
  margin-left: 8px;
}

/* Logo 图片:固定高度 30px */
.logo {
  height: 30px;
}
</style>