/**
 * ====================================================================
 * api/product.js —— 商品 / 购物车 / 订单模块的后端接口请求封装
 * ====================================================================
 * 职责:把“商品创建管理、商品浏览、购物车、订单、支付”相关接口统一
 *      封装为异步函数,各页面调用时只需关心参数与返回,不必接触 axios。
 * 说明:
 *   - 统一使用 src/request.js 创建的 axios 实例 myAxios(token 由拦截器
 *     自动携带,baseURL 指向 Flask 后端);
 *   - 带商品/订单 id 的接口,id 通过模板字符串拼进 URL 路径;
 *   - 创建/编辑商品可能携带图片文件,使用 FormData 请求体,浏览器会自动
 *     设置 Content-Type,无需手动指定;
 *   - 后端返回统一为 { code, data, message },code === 0 表示成功。
 */
import myAxios from "../request";

// 后端接口:POST /product/create(卖家发布新商品,支持 FormData 携带图片)
// 创建商品
export const createProduct = async (data) => {
    return await myAxios.request({
        url: '/product/create',
        method: 'POST',
        data: data
        // 注意：使用 FormData 时，不需要手动设置 Content-Type 头，浏览器会自动设置
    })
}

// 后端接口:GET /seller/products/profile(卖家分页查询自己发布的商品)
// 商家查询自己商品（支持分页和过滤）
export const getSellerProducts = async (params) => {
    return await myAxios.request({
        url: '/seller/products/profile',
        method: 'GET',
        params: params   // GET 请求参数通过 params 传递
    })
}

// 后端接口:GET /user/products/profile(买家分页浏览全部在售商品)
// 用户查询所有商品（支持分页和过滤）
export const getUserProducts = async (params) => {
    return await myAxios.request({
        url: '/user/products/profile',
        method: 'GET',
        params: params
    })
}

// 后端接口:DELETE /product/delete/<productId>(按商品 id 删除)
// 删除商品
export const deleteProduct = async (productId) => {
    return await myAxios.request({
        url: `/product/delete/${productId}`,
        method: 'DELETE'
    })
}

// 后端接口:PUT /product/update/<productId>(按商品 id 编辑,支持 FormData 携带图片)
// 编辑商品
export const updateProduct = async (productId, data) => {
    // 检查 data 是否为 FormData
    if (data instanceof FormData) {
        return await myAxios.request({
            url: `/product/update/${productId}`,
            method: 'PUT',
            data: data
            // 注意：使用 FormData 时，不需要手动设置 Content-Type 头，浏览器会自动设置
        })
    } else {
        return await myAxios.request({
            url: `/product/update/${productId}`,
            method: 'PUT',
            data: data
        })
    }
}

// 后端接口:POST /user/add_to_shopping_car/<productId>(把指定商品加入购物车,quantity 为数量)
// 加入购物车
export const addToCart = async (productId, quantity = 1) => {
    return await myAxios.request({
        url: `/user/add_to_shopping_car/${productId}`,
        method: 'POST',
        data: {
            quantity: quantity
        }
    })
}

// 后端接口:GET /user/shopping_cart_profile(获取当前买家的购物车内容)
// 获取用户购物车
export const getCartProfile = async () => {
    return await myAxios.request({
        url: '/user/shopping_cart_profile',
        method: 'GET'
    })
}

// 后端接口:PUT /user/shopping_cart_update/<productId>(修改购物车中该商品的数量)
// 更新购物车商品数量
export const updateCartItem = async (productId, quantity) => {
    return await myAxios.request({
        url: `/user/shopping_cart_update/${productId}`,
        method: 'PUT',
        data: {
            quantity: quantity
        }
    })
}

// 后端接口:POST /user/create_order(把当前购物车内容结算生成订单)
// 创建订单
export const createOrder = async () => {
    return await myAxios.request({
        url: '/user/create_order',
        method: 'POST'
    })
}

// 后端接口:GET /user/profile_order(分页查询当前买家的订单列表)
// 获取用户订单列表
export const getUserOrders = async (params) => {
    return await myAxios.request({
        url: '/user/profile_order',
        method: 'GET',
        params: params
    })
}

// 后端接口:GET /user/profile_order/<orderId>(查看单个订单的详情)
// 获取订单详情
export const getOrderDetail = async (orderId) => {
    return await myAxios.request({
        url: `/user/profile_order/${orderId}`,
        method: 'GET'
    })
}

// 后端接口:POST /api/pay/prepare(向支付平台发起预支付,返回支付/签名链接)
// 支付准备（生成签名支付链接）
export const preparePayment = async (orderId) => {
    return await myAxios.request({
        url: '/api/pay/prepare',
        method: 'POST',
        data: {
            order_id: orderId
        }
    })
}

