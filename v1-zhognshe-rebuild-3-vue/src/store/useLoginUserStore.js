/**
 * ====================================================================
 * store/useLoginUserStore.js —— 登录用户全局状态仓库（Pinia）
 * ====================================================================
 * 作用：把“当前登录用户”这一全站共享数据放进统一的 Store，
 *       导航栏用户名显示、路由守卫的角色判断等都能从这里读取，
 *       避免各个页面各自请求、各自保存导致状态不一致。
 * 本仓库采用 Pinia 的“组合式（setup）”写法：
 *   - state  ：loginUser（当前登录用户对象；未登录时默认为
 *              { username: '未登录' }）；
 *   - actions：fetchLoginUser() —— 向后端拉取当前登录用户信息；
 *              setLoginUser()   —— 登录/注册成功后由前端直接赋值。
 * 补充：token 本身存放在 localStorage，由 axios 拦截器统一携带，
 *       本仓库只保存用户信息，不直接持久化 token。
 */
import {defineStore} from "pinia";
import {ref} from "vue";
// 获取当前用户信息的接口封装（对应 GET /user/profile）
import {userProfile} from "@/api/user.js";
// 获取当前后台账号信息的接口封装（对应 GET /api/staff/me，管理员/审计员用）
import {staffMe} from "@/api/staff.js";

// 定义名为 loginUser 的仓库；组件内通过 useLoginUserStore() 获取仓库实例
export const useLoginUserStore = defineStore('loginUser', () => {

  // —— state：当前登录用户 ——
  // 默认值：未登录占位对象；登录成功后被后端返回的用户对象整体替换
  const loginUser = ref({
      username: '未登录',
  })

  /**
   * —— action：向后端获取当前登录用户信息（GET /user/profile）——
   * 成功时（res.data.code === 0 且有数据）用返回数据整体覆盖 loginUser；
   * 请求异常时若返回 401（token 失效/未授权），把状态复位为“未登录”。
   */
  async function fetchLoginUser() {
       try {
           const res = await userProfile();
           if (res.data.code === 0 && res.data.data) {
               loginUser.value = res.data.data;
           }
       } catch (error) {
           // 处理未授权错误，设置为未登录状态
           if (error.response && error.response.status === 401) {
               loginUser.value = {
                   username: '未登录',
               };
           }
           console.error('获取用户信息失败:', error);
       }
  }

  /**
   * —— action：直接设置登录用户信息 ——
   * 供登录/注册流程成功后，由前端把返回的用户对象直接写入仓库
   * （无需再额外请求后端接口）。
   */
  function  setLoginUser(newLoginUser) {
      loginUser.value = newLoginUser;
  }

  /**
   * —— action：获取当前后台账号信息（admin/auditor，GET /api/staff/me）——
   * 后台页面（/admin*、/auditor*、/staff*）刷新后恢复登录态时由路由守卫调用；
   * 后台账号与前台 user/seller 是两套账户体系，因此不能复用 /user/profile。
   */
  async function fetchStaffMe() {
       try {
           const res = await staffMe();
           if (res.data.code === 0 && res.data.data) {
               loginUser.value = {
                   username: res.data.data.username,
                   role: res.data.data.role,
                   // 是否已绑定 TOTP：路由守卫据此把未绑定的后台账号拦到绑定页
                   totp_enabled: res.data.data.totp_enabled,
               };
           }
       } catch (error) {
           // 401（token 失效/未授权）时复位为未登录（request.js 会顺带跳登录页）
           if (error.response && error.response.status === 401) {
               loginUser.value = {username: '未登录'};
           }
           console.error('获取后台账号信息失败:', error);
       }
  }

  // —— 对外暴露：状态 + 动作 ——
  // 组件中 const store = useLoginUserStore() 后即可读写 store.loginUser
  return { loginUser , fetchLoginUser , setLoginUser , fetchStaffMe };
})
