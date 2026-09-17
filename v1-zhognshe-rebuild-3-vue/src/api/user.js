/**
 * ====================================================================
 * api/user.js —— 用户模块后端接口的请求封装
 * ====================================================================
 * 职责：把“注册、登录、个人资料、注销、证书登录”等用户相关接口
 *       统一封装成可复用的异步函数，页面与 Store 只需调用函数并
 *       传入参数，不必关心 axios 的细节。
 * 说明：
 *   - 所有请求都走 src/request.js 创建的 axios 实例 myAxios
 *     （baseURL 指向 Flask 后端，token 由拦截器自动附加，无需重复设置）；
 *   - 后端返回统一为 { code, data, message }，其中 code === 0 表示成功；
 *   - 约定：GET 请求参数放在 params；POST / PUT / DELETE 的请求体
 *     放在 data。
 */
import myAxios from "../request";

/**
 * 用户注册：POST /user/register
 * params：注册表单数据（用户名、密码等）；
 * 说明：responseType: 'blob' 表示把响应按二进制流接收（不按 JSON 解析），
 *       适用于接口返回文件 / 图片等二进制内容的场景。
 */
export const userRegister = async (params) => {
    return await myAxios.request({
        url: '/user/register',
        method: 'POST',
        data: params,
        responseType: 'blob'
    })
}

/**
 * 用户登录：POST /user/login
 * params：登录表单（用户名、密码等）；
 * 成功返回的 token 由调用方保存到 localStorage，供后续请求使用。
 */
export const userLogin = async (params) => {
    return await myAxios.request({
        url: '/user/login',
        method: 'POST',
        data: params
    })
}

/**
 * 获取当前登录用户信息：GET /user/profile
 * 供 Pinia Store 的 fetchLoginUser() 调用，用于填充全局登录用户状态；
 * 一般无需传参，接口根据请求头携带的 token 识别当前用户。
 */
export const userProfile = async (params) => {
    return await myAxios.request({
        url: '/user/profile',
        method: 'GET',
        params: params
    })
}

/**
 * 修改用户信息：PUT /user/update
 * params：要修改的字段（如昵称、头像、密码等）。
 */
export const userUpdate = async (params) => {
    return await myAxios.request({
        url: '/user/update',
        method: 'PUT',
        data: params
    })
}

/**
 * 删除（注销）用户账号：DELETE /user/delete
 * params：删除账号所需的确认信息。
 */
export const userDelete = async (params) => {
    return await myAxios.request({
        url: '/user/delete',
        method: 'DELETE',
        data: params
    })


}

/**
 * 用户退出登录：POST /user/logout
 * 通知后端注销当前会话；前端随后清理本地登录状态。
 */
export const userLogOut = async (params) => {
    return await myAxios.request({
        url: '/user/logout',
        method: 'POST',
        data: params
    })
}

/**
 * 证书登录：POST /user/certLogin
 * 基于数字证书的免密登录入口：formData 为 multipart/form-data 上传的
 * 证书等文件数据，故需手动指定 Content-Type 为 multipart/form-data。
 */
export const userCertLogin = async (formData) => {
    return await myAxios.request({
        url: '/user/certLogin',
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}
