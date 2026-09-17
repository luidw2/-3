/**
 * ====================================================================
 * router/index.js —— 前端路由配置（页面映射 + 导航守卫）
 * ====================================================================
 * 职责：
 *   1. 集中登记系统中所有页面的“路径 → 组件”对应关系；
 *   2. 通过路由 meta 元信息声明页面访问要求：
 *        - requiresAuth: true  ：必须登录后才能访问；
 *        - roles: [...]        ：仅允许指定角色访问
 *          （'seller' 为卖家，'user' 为买家，实现角色权限控制）；
 *   3. 定义全局前置守卫 beforeEach，在每次跳转前完成
 *      “登录校验 + 角色权限校验”两道检查；
 *   4. createWebHistory()：采用 HTML5 History 模式（URL 不带 # 号）。
 * 关联机制：
 *   - 登录用户信息存于 Pinia Store（useLoginUserStore）；
 *   - token 存于 localStorage，由 axios 拦截器统一携带。
 */
import {createRouter, createWebHistory} from 'vue-router'
// —— 页面组件导入：下方组件分别对应路由表中登记的各个页面 ——
import HomePage from "@/pages/HomePage.vue";
import UserLoginPage from "@/pages/user/UserLoginPage.vue";
import UserRegisterPage from "@/pages/user/UserRegisterPage.vue";
import UserProfilePage from "@/pages/user/UserProfilePage.vue";
import UserUpdatePage from "@/pages/user/UserUpdataPage.vue";
import UserDeletePage from "@/pages/user/UserDeletePage.vue";
import UserCertLoginPage from "@/pages/user/UserCertLoginPage.vue";
import ProductCreatePage from "@/pages/user/ProductCreatePage.vue";
import SellerProductManagePage from "@/pages/user/SellerProductManagePage.vue"
import UserProductBrowsePage from  "@/pages/user/UserProductBrowsePage.vue"
import ProfileCart from "@/pages/user/ProfileCart.vue";
import ProfileOrder from "@/pages/user/ProfileOrder.vue";
// —— 后台（staff）页面：管理员/审计员登录、TOTP 绑定与管理页面 ——
import StaffLoginPage from "@/pages/staff/StaffLoginPage.vue";
import TotpBindPage from "@/pages/staff/TotpBindPage.vue";
import AdminAccountsPage from "@/pages/staff/AdminAccountsPage.vue";
import AdminProductsPage from "@/pages/staff/AdminProductsPage.vue";
import AuditLogPage from "@/pages/staff/AuditLogPage.vue";
import {message} from "ant-design-vue";
import {useLoginUserStore} from "@/store/useLoginUserStore";

const routes = [
    {
        // 【首页】路径 '/';组件 HomePage;守卫要求:无;
        // 对应顶部导航“主页”菜单,是所有用户进入系统的默认落地页。
        path: '/',
        name: 'home',
        component: HomePage
    },
    {
        // 【用户登录】路径 '/user/login';组件 UserLoginPage;守卫要求:无;
        // 未登录用户访问受保护页面时,会被全局守卫重定向回本页。
        path: '/user/login',
        name: 'userLogin',
        component: UserLoginPage
    },
    {
        // 【用户注册】路径 '/user/register';组件 UserRegisterPage;守卫要求:无。
        path: '/user/register',
        name: 'userRegister',
        component: UserRegisterPage
    },
    {
        // 【个人中心】路径 '/user/profile';组件 UserProfilePage;
        // 守卫要求:meta.requiresAuth = true → 必须登录;
        // 菜单意义:顶部导航常驻菜单项,展示/管理当前账号资料。
        path: '/user/profile',
        name: 'userProfile',
        component: UserProfilePage,
        meta: {
            requiresAuth: true,
        },
    },
    {
        // 【修改资料】路径 '/user/update';组件 UserUpdatePage;
        // 守卫要求:requiresAuth → 必须登录(个人中心下的“编辑资料”)。
        path: '/user/update',
        name: 'userUpdate',
        component: UserUpdatePage,
        meta: {
            requiresAuth: true,
        },
    },
    {
        // 【注销账号】路径 '/user/delete';组件 UserDeletePage;
        // 守卫要求:requiresAuth → 必须登录(个人中心下的“删除账号”)。
        path: '/user/delete',
        name: 'userDelete',
        component: UserDeletePage,
        meta: {
            requiresAuth: true,
        },
    },
    {
        // 【证书登录】路径 '/user/certLogin';组件 UserCertLoginPage;守卫要求:无;
        // 基于数字证书的免密登录入口,与账号密码登录并列的另一种认证方式。
        path: '/user/certLogin',
        name: 'certLogin',
        component: UserCertLoginPage
    },
    {
        // 【创建商品】路径 '/product/create';组件 ProductCreatePage;
        // 守卫要求:requiresAuth + roles:['seller'] → 仅卖家可访问;
        // 菜单意义:卖家登录后顶部导航“创建商品”菜单项。
        path: '/product/create',
        name: 'productCreate',
        component: ProductCreatePage,
        meta: {
            requiresAuth: true,
            roles: ['seller'],
        },
    },
    {
        // 【卖家商品管理】路径 '/seller/products/profile';
        // 组件 SellerProductManagePage;
        // 守卫要求:requiresAuth + roles:['seller'] → 仅卖家可访问;
        // 菜单意义:卖家查看/管理自己发布商品的页面。
        path: '/seller/products/profile',
        name: 'sellerProducts',
        component: SellerProductManagePage,
        meta: {
            requiresAuth: true,
            roles: ['seller'],
        },
    },
    {
        // 【买家商品浏览】路径 '/user/products/profile';
        // 组件 UserProductBrowsePage;
        // 守卫要求:requiresAuth + roles:['user'] → 仅买家可访问;
        // 菜单意义:买家浏览/搜索商品并下单的页面。
        path: '/user/products/profile',
        name: 'UserProducts',
        component: UserProductBrowsePage,
        meta: {
            requiresAuth: true,
            roles: ['user'],
        },
    },
    {
        // 【购物车】路径 '/user/shopping_cart_profile';组件 ProfileCart;
        // 守卫要求:requiresAuth + roles:['user'] → 仅买家可访问;
        // 菜单意义:买家查看购物车、调整数量并结算下单。
        path: '/user/shopping_cart_profile',
        name: 'UserCart',
        component: ProfileCart,
        meta: {
            requiresAuth: true,
            roles: ['user'],
        },
    },
    {
        // 【我的订单】路径 '/user/profile_order';组件 ProfileOrder;
        // 守卫要求:requiresAuth + roles:['user'] → 仅买家可访问;
        // 菜单意义:买家查看订单列表与订单详情。
        path: '/user/profile_order',
        name: 'UserOrders',
        component: ProfileOrder,
        meta: {
            requiresAuth: true,
            roles: ['user'],
        },
    },
    // ---------- 后台（staff）路由：管理员 / 审计员 ----------
    {
        // 【后台登录】路径 '/staff/login';组件 StaffLoginPage;守卫要求:无;
        // 管理员/审计员的两步登录入口(密码 → TOTP 动态码/恢复码)。
        path: '/staff/login',
        name: 'staffLogin',
        component: StaffLoginPage,
    },
    {
        // 【TOTP 绑定】路径 '/staff/totp/setup';组件 TotpBindPage;
        // 守卫要求:requiresAuth + roles:['admin','auditor'] → 仅后台账号可访问。
        path: '/staff/totp/setup',
        name: 'totpBind',
        component: TotpBindPage,
        meta: {
            requiresAuth: true,
            roles: ['admin', 'auditor'],
        },
    },
    {
        // 【账号管理】路径 '/admin/accounts';组件 AdminAccountsPage;
        // 守卫要求:requiresAuth + roles:['admin'] → 仅管理员可访问。
        path: '/admin/accounts',
        name: 'adminAccounts',
        component: AdminAccountsPage,
        meta: {
            requiresAuth: true,
            roles: ['admin'],
        },
    },
    {
        // 【商品管理】路径 '/admin/products';组件 AdminProductsPage;
        // 守卫要求:requiresAuth + roles:['admin'] → 仅管理员可访问。
        path: '/admin/products',
        name: 'adminProducts',
        component: AdminProductsPage,
        meta: {
            requiresAuth: true,
            roles: ['admin'],
        },
    },
    {
        // 【审计日志】路径 '/auditor/logs';组件 AuditLogPage;
        // 守卫要求:requiresAuth + roles:['auditor'] → 仅审计员可访问(只读)。
        path: '/auditor/logs',
        name: 'auditorLogs',
        component: AuditLogPage,
        meta: {
            requiresAuth: true,
            roles: ['auditor'],
        },
    },
]

// ---------- 创建路由实例 ----------
// createWebHistory():使用 HTML5 History 模式,地址栏 URL 不带 # 号;
// routes 即上方定义的路由表。
const router = createRouter({
    history: createWebHistory(),
    routes
})

// ---------- 全局前置守卫:每次路由跳转前都会执行 ----------
// 负责两道检查:① 登录校验(未登录拦截并跳转登录页);
//             ② 角色权限校验(角色不满足页面要求则跳回首页)。
router.beforeEach(async (to) => {
    // ① 页面未声明 requiresAuth(不需要登录)→ 直接放行
    const requiresAuth = Boolean(to.meta?.requiresAuth);
    if (!requiresAuth) {
        return true;
    }

    // ② 登录校验:localStorage 中没有 token → 视为未登录,提示并跳转登录页
    const token = localStorage.getItem('token');
    if (!token) {
        message.error("请先登录");
        return {name: 'userLogin'};
    }

    // ③ 获取当前用户角色与状态
    //    后台页面(管理员/审计员)走 /api/staff/me,商城页面走 /user/profile ——
    //    两套账户体系接口不同,不能混用;后台每次进入都拉一次最新状态
    //   (角色 + TOTP 绑定状态),避免使用缓存角色导致判断过时
    const loginUserStore = useLoginUserStore();
    const isStaffRoute = ['/staff', '/admin', '/auditor'].some(p => to.path.startsWith(p));
    let currentRole = loginUserStore.loginUser?.role;
    if (isStaffRoute) {
      await loginUserStore.fetchStaffMe();
      // ③-1 双因素门槛:后台账号未绑定 TOTP → 不允许使用任何后台功能,
      //     强制去绑定页(绑定页本身豁免,避免死循环);
      //     真正的拦截在后端(totp_ok 声明),这里只是引导,不让用户撞 403
      if (to.path !== '/staff/totp/setup' &&
          ['admin', 'auditor'].includes(loginUserStore.loginUser?.role) &&
          loginUserStore.loginUser?.totp_enabled === false) {
        message.warning('请先完成 TOTP 绑定后再使用后台功能');
        return {path: '/staff/totp/setup'};
      }
    } else if (!currentRole) {
      await loginUserStore.fetchLoginUser();
    }
    currentRole = loginUserStore.loginUser?.role;

    // ④ 角色校验:页面通过 meta.roles 声明允许访问的角色,
    //    若当前用户角色不在允许列表中 → 提示无权限并跳回首页;
    //    若在允许列表中则继续向下执行,最终放行进入页面。
    const allowedRoles = to.meta?.roles;
    if (Array.isArray(allowedRoles) && allowedRoles.length > 0 && !allowedRoles.includes(currentRole)) {
        message.error("无权限访问该页面");
        return {name: 'home'};
    }

    return true;
});

// 导出路由实例,供 main.js 中 app.use(router) 全局注册使用
export default router
