/**
 * 统一 HTTP 请求封装（基于 axios）
 *
 * 本地开发方案：前端(127.0.0.1:5173) 与后端 Flask(127.0.0.1:5000) 分离运行，
 * 本文件决定所有接口请求发往哪个后端地址，以及静态资源图片的完整 URL 拼法。
 *
 * 后端地址配置规则（优先级从高到低）：
 *   1. 环境变量 VITE_API_BASE_URL —— 可在 前端根目录/.env.local 中设置以覆盖默认值；
 *   2. 代码默认值 http://127.0.0.1:5000（本地开发，不再依赖 cpolar 内网穿透）。
 * 若后端更换端口或部署到其它主机/公网，只需修改这一处（或通过 .env.local 覆盖）。
 */
import axios from "axios";
import {message} from "ant-design-vue";

// 后端接口基础地址：本地开发时直连本机 Flask 服务
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

/**
 * 把后端返回的相对路径（如 '/static/uploads/xx.png'）拼成可访问的完整 URL。
 * 组件里展示商品/订单图片时使用：<img :src="getApiUrl(record.image_url)" />
 * 传入的若已是 http(s) 完整地址则原样返回，避免二次拼接。
 */
export const getApiUrl = (path = '') => {
  if (!path) {
    return '';
  }
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  return `${API_BASE_URL.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`;
};

// 创建 axios 实例：业务模块（src/api/*.js）只需写 '/user/xxx' 等相对路径，自动拼上 API_BASE_URL
const myAxios = axios.create({
  baseURL: API_BASE_URL,                    // 接口前缀（后端地址）
  timeout: 100000,                          // 请求超时（毫秒）：大文件上传/证书登录耗时较长
  headers: {'X-Custom-Header': 'foobar'}    // 预留的自定义请求头
});

// ---------- 请求拦截器：每次发请求前自动携带登录令牌 ----------
myAxios.interceptors.request.use(function (config) {
    // 从 localStorage 读取 JWT（登录成功时由下面的响应拦截器写入）
    const token = localStorage.getItem('token');
    if (token) {
      // 后端通过 Authorization: Bearer <token> 识别当前用户（见后端 jwt_auth 中间件）
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }, function (error) {
    // 请求构造阶段出错（如配置非法），直接抛给调用方处理
    return Promise.reject(error);
  });

// ---------- 响应拦截器：统一处理"登录成功保存 token"与"401 未登录跳转" ----------
myAxios.interceptors.response.use(function (response) {
    // HTTP 2xx 都会进入这里
    // 登录接口成功（code === 0）时把 access_token 保存到 localStorage
    if (response.config.url === '/user/login' && response.data.code === 0) {
      if (response.data.data && response.data.data.access_token) {
        localStorage.setItem('token', response.data.data.access_token);
      }
    }
    return response;
  }, function (error) {
    // 非 2xx 响应或网络错误进入这里
    if (error.response && error.response.status === 401) {
      // 401 未授权：token 缺失/过期，清除本地 token 并跳回对应登录页
      // 后台账号（staff/admin/auditor 路径）跳后台登录页，前台用户跳用户登录页
      const pathname = window.location.pathname;
      const isStaffPage = pathname.startsWith('/staff') || pathname.startsWith('/admin') || pathname.startsWith('/auditor');
      const loginPath = isStaffPage ? '/staff/login' : '/user/login';
      localStorage.removeItem('token');
      if (pathname !== loginPath) {
        window.location.replace(loginPath);
      }
    }
    return Promise.reject(error);
  });

// 默认导出实例；所有 api 模块（src/api/*.js）统一从这里引入
export default myAxios;
