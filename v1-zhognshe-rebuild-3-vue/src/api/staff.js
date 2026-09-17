/**
 * staff.js —— 后台账号（管理员 / 审计员）接口封装
 * ====================================================================
 * 对应后端 app/api/staff/ 下四类接口：
 *   1. 认证登录类：密码第一步 / TOTP 动态码第二步 / 恢复码第二步 / me / logout
 *   2. TOTP 绑定类：setup 生成绑定材料 / confirm 确认绑定
 *   3. 管理员类：账号管理（user/seller 的禁用、启用、删除）+ 商品管理
 *   4. 审计员类：审计日志分页查询 / CSV 导出
 * 约定：后端成功时 res.data.code === 0；HTTP 层统一由 request.js 拦截器处理。
 */
import myAxios from "../request";

// ---------- 1. 后台登录（两步） ----------
// 第一步：密码验证。返回 need_totp + step_token（或未绑定时的 access_token）
export const staffLogin = (params) => {
    return myAxios.request({ url: '/api/staff/login', method: 'POST', data: params })
}

// 第二步：TOTP 动态码换正式令牌（{ step_token, code }）
export const staffLoginTotp = (params) => {
    return myAxios.request({ url: '/api/staff/login/totp', method: 'POST', data: params })
}

// 第二步（备选）：一次性恢复码登录（{ step_token, code }）
export const staffLoginRecovery = (params) => {
    return myAxios.request({ url: '/api/staff/login/recovery', method: 'POST', data: params })
}

// 当前后台账号信息（GET /api/staff/me）：刷新页面恢复登录态用
export const staffMe = () => {
    return myAxios.request({ url: '/api/staff/me', method: 'GET' })
}

// 退出登录（服务端只记审计，前端负责清除 token）
export const staffLogout = () => {
    return myAxios.request({ url: '/api/staff/logout', method: 'POST' })
}

// ---------- 2. TOTP 绑定 ----------
// 生成绑定材料：返回 secret / otpauth_uri（二维码）/ recovery_codes（仅此一次）
export const totpSetup = () => {
    return myAxios.request({ url: '/api/staff/totp/setup', method: 'POST', data: {} })
}

// 确认绑定：{ secret, code }，成功后服务端加密落库并启用 TOTP
export const totpConfirm = (params) => {
    return myAxios.request({ url: '/api/staff/totp/confirm', method: 'POST', data: params })
}

// ---------- 3. 管理员接口 ----------
// 账号列表（type: user | seller | all）
export const adminListAccounts = (params) => {
    return myAxios.request({ url: '/api/admin/users', method: 'GET', params: params })
}

// 禁用 / 启用账号（type: 'user' 或 'seller'，后端对应 users/sellers 两组路由）
export const adminDisableAccount = (type, id) => {
    return myAxios.request({ url: `/api/admin/${type}s/${id}/disable`, method: 'POST' })
}
export const adminEnableAccount = (type, id) => {
    return myAxios.request({ url: `/api/admin/${type}s/${id}/enable`, method: 'POST' })
}

// 删除账号（级联清理其名下数据）
export const adminDeleteAccount = (type, id) => {
    return myAxios.request({ url: `/api/admin/${type}s/${id}`, method: 'DELETE' })
}

// 商品列表（分页 + status/name_keyword 过滤）/ 删除任意商品
export const adminListProducts = (params) => {
    return myAxios.request({ url: '/api/admin/products', method: 'GET', params: params })
}
export const adminDeleteProduct = (id) => {
    return myAxios.request({ url: `/api/admin/products/${id}`, method: 'DELETE' })
}

// ---------- 4. 审计员接口 ----------
// 分页/过滤查询审计日志（event_type / start / end 可选）
export const auditorListEvents = (params) => {
    return myAxios.request({ url: '/api/auditor/events', method: 'GET', params: params })
}

// 导出审计日志 CSV（responseType: 'blob'，前端触发文件下载）
export const auditorExport = (params) => {
    return myAxios.request({
        url: '/api/auditor/export',
        method: 'GET',
        params: params,
        responseType: 'blob'
    })
}
