<template>
  <div id="profileCartPage">
    <div class="cart-container">
      <h2 class="title">我的购物车</h2>

      <!-- 购物车为空时显示 -->
      <a-empty v-if="!loading && cartItems.length === 0" description="购物车是空的">
        <a-button type="primary" @click="goShopping">去购物</a-button>
      </a-empty>

      <!-- 购物车商品列表 -->
      <div v-else>
        <!-- 顶部统计栏：总件数与总金额由计算属性实时计算（只统计在售商品） -->
        <div class="cart-summary">
          <span>共 {{ totalItems }} 件商品</span>
          <span class="total-price">总价：{{ (totalPrice / 100).toFixed(2) }} 元</span>
        </div>

        <a-table
          :columns="columns"
          :data-source="cartItems"
          :loading="loading"
          row-key="cart_item_id"
          bordered
          :pagination="false"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'image_url'">
              <template v-if="record.image_url">
                <img :src="getApiUrl(record.image_url)" style="width: 60px; height: 60px; object-fit: cover" />
              </template>
              <template v-else>
                <span>无照片</span>
              </template>
            </template>
            <template v-if="column.key === 'product_name'">
              <span :class="{ 'unavailable': !record.available }">{{ record.product_name }}</span>
              <a-tag v-if="!record.available" color="red" style="margin-left: 8px">商品已下架</a-tag>
            </template>
            <template v-if="column.key === 'price'">
              {{ (record.price / 100).toFixed(2) }} 元
            </template>
            <template v-if="column.key === 'quantity'">
              {{ record.quantity }}
            </template>
            <template v-if="column.key === 'subtotal'">
              {{ (record.subtotal / 100).toFixed(2) }} 元
            </template>
            <template v-if="column.key === 'action'">
              <a-button type="link" danger size="small" @click="handleEditItem(record)">修改</a-button>
            </template>
          </template>
        </a-table>

        <!-- 底部操作区：左边“继续购物”，右边“去结算”（无可用商品时按钮自动禁用） -->
        <div class="cart-actions">
          <a-button @click="goShopping">继续购物</a-button>
          <a-button type="primary" :disabled="availableItems.length === 0" @click="handleCheckout">
            去结算 ({{ totalItems }} 件商品)
          </a-button>
        </div>
      </div>

      <!-- 结算确认弹窗 -->
      <a-modal
        v-model:open="checkoutModalVisible"
        title="确认订单"
        :maskClosable="true"
      >
        <!-- 结算清单：逐行列出可结算商品的名称 / 数量 / 小计，供用户下单前确认 -->
        <div class="checkout-detail">
          <div class="checkout-item" v-for="item in availableItems" :key="item.cart_item_id">
            <span class="checkout-name">{{ item.product_name }}</span>
            <span class="checkout-qty">x {{ item.quantity }}</span>
            <span class="checkout-price">{{ (item.subtotal / 100).toFixed(2) }} 元</span>
          </div>
          <a-divider />
          <div class="checkout-total">
            <span>订单总价：</span>
            <span class="checkout-total-price">{{ (totalPrice / 100).toFixed(2) }} 元</span>
          </div>
        </div>
        <template #footer>
          <a-button type="primary" :loading="checkoutLoading" @click="handleConfirmCheckout">确定</a-button>
        </template>
      </a-modal>

      <!-- 修改商品弹窗 -->
      <a-modal
        v-model:open="editModalVisible"
        title="修改商品数量"
        @ok="handleSaveEdit"
        @cancel="handleCancelEdit"
      >
        <!-- 修改商品表单：名称 / 图片 / 单价只读展示；数量可编辑，小计随数量实时计算 -->
        <a-form
          :model="editForm"
          layout="vertical"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 18 }"
        >
          <a-form-item label="商品名称">

            <span style="color: #000000; font-weight: 600;">
              {{ editForm.product_name}}
            </span>
          </a-form-item>
          <a-form-item label="商品图片">
            <template v-if="editForm.image_url">
              <img :src="getApiUrl(editForm.image_url)" style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px;" />
            </template>
            <template v-else>
              <span style="color: #999;">无照片</span>
            </template>
          </a-form-item>
          <a-form-item label="单价">
            <span>{{ (editForm.price / 100).toFixed(2) }} 元</span>
          </a-form-item>
          <a-form-item label="商品数量">
            <a-input-number
              v-model:value="editForm.quantity"
              :min="0"
            />
          </a-form-item>
          <a-form-item label="小计">
            <span style="color: #e9c63b; font-weight: 600;">
              {{ ((editForm.price * editForm.quantity) / 100).toFixed(2) }} 元
            </span>
          </a-form-item>
        </a-form>
      </a-modal>
    </div>
  </div>
</template>

<script lang="ts" setup>
// ============================================================
// 页面：购物车（ProfileCart.vue）
// 讲解要点：
//   1. 数据流：进入页面 onMounted → fetchCart() 拉取购物车列表 →
//      用户操作（修改数量 / 去结算）→ 调用后端接口 → 更新本地数据或跳转页面。
//   2. 金额计算：后端金额统一以“分”存储，展示时用 (金额 / 100).toFixed(2)
//      转成“元”；小计 = 单价 × 数量，总价由计算属性 totalPrice 实时求和。
//   3. 结算流程：点“去结算”→ 弹出确认订单弹窗 → 点“确定”→ 调 createOrder()
//      由后端把购物车商品生成订单 → 成功后跳转“我的订单”页并刷新购物车。
//   4. 有效性过滤：只对 available=true 的在售商品统计件数 / 金额 / 允许结算，
//      已下架商品仅在列表中提示“商品已下架”，不参与计价。
// ============================================================
import { ref, reactive, computed, onMounted } from 'vue'; // Vue 组合式 API：ref / reactive 声明响应式数据，computed 派生计算属性，onMounted 挂载钩子
import { message } from 'ant-design-vue'; // Ant Design Vue 消息提示（成功 / 失败 / 网络错误提示）
import { useRouter } from 'vue-router';   // 路由实例，负责页面跳转（去购物、结算后跳订单页）
import { getCartProfile, updateCartItem, createOrder } from '@/api/product'; // 购物车查询 / 修改数量 / 创建订单 三个后端接口封装
import { getApiUrl } from '@/request';    // 把后端返回的相对图片路径拼接成完整可访问 URL

// 购物车条目的数据结构（与后端返回 items 中每个元素一一对应）
interface CartItem {
  cart_item_id: number;    // 购物车条目 ID（表格行 key）
  product_id: number;      // 商品 ID（修改数量时作为接口参数传给后端）
  product_name: string;    // 商品名称
  quantity: number;        // 购买数量（可修改，改为 0 表示删除该商品）
  price: number;           // 商品单价（单位：分）
  image_url: string | null; // 商品图片相对路径，可能为空（为空时页面显示“无照片”）
  subtotal: number;        // 小计 = 单价 × 数量（单位：分，后端返回）
  available: boolean;      // 商品是否在售：下架商品不计入结算与金额统计
  created_at: string | null; // 创建时间（暂未展示）
  updated_at: string | null; // 最近更新时间（暂未展示）
}

const router = useRouter();               // 路由实例：用于“去购物”与结算成功后跳转订单页
const loading = ref(false);               // 购物车列表加载中标志（驱动表格 loading 与空态判断）
const cartItems = ref<CartItem[]>([]);    // 购物车商品列表（页面核心数据，接口返回后缓存于此）

// —— 结算确认弹窗状态 ——
const checkoutModalVisible = ref(false);  // 结算弹窗是否显示

// —— “修改数量”弹窗状态 ——
const editModalVisible = ref(false);      // 修改弹窗是否显示
// 修改弹窗表单：点“修改”时把选中行数据回填进来，保存时提交给后端
const editForm = reactive({
  cart_item_id: 0,                 // 正在修改的购物车条目 ID（保存 / 删除时用来定位本地数据）
  product_name: '',                // 商品名称（弹窗内只读展示）
  price: 0,                        // 商品单价（单位：分，弹窗内只读展示）
  quantity: 1,                     // 可编辑的新数量：改为 0 表示删除该商品
  image_url: null as string | null // 商品图片相对路径（弹窗内只读展示）
});

// 购物车表格列配置：dataIndex 绑定数据字段，key 供 bodyCell 自定义单元格内容
const columns = [
  { title: '商品照片', dataIndex: 'image_url', key: 'image_url', width: 100 },
  { title: '商品名称', key: 'product_name', width: 250 },
  { title: '单价', key: 'price', width: 120 },
  { title: '数量', key: 'quantity', width: 120 },
  { title: '小计', key: 'subtotal', width: 120 },
  { title: '操作', key: 'action', width: 100 },
];

// —— 计算属性（派生数据）：均只统计“在售商品”，保证下架商品不参与计价 ——
// 可结算商品集合：过滤出 available=true 的条目（结算只针对这些商品）
const availableItems = computed(() => cartItems.value.filter(item => item.available));
// 可结算商品总件数：各商品数量之和（顶部统计栏与“去结算”按钮文案共用）
const totalItems = computed(() => availableItems.value.reduce((sum, item) => sum + item.quantity, 0));
// 可结算商品总金额：各商品小计之和（单位：分），顶部总价与结算弹窗总价均由它派生
const totalPrice = computed(() => availableItems.value.reduce((sum, item) => sum + item.subtotal, 0));

// 拉取购物车数据：调用 getCartProfile()，后端约定 code===200 表示成功，
// 成功后把返回的 items 列表缓存进 cartItems，表格与计算属性随之自动更新
const fetchCart = async () => {
  loading.value = true;   // 开启加载态（表格转圈，也防止空态误判）
  try {
    const res = await getCartProfile(); // 请求“获取当前用户购物车”接口
    if (res.data.code === 200) {
      cartItems.value = res.data.data.items || []; // 取购物车条目列表
    } else {
      message.error(res.data.message || '获取购物车失败'); // 业务失败：提示后端返回的 message
    }
  } catch (error: any) {
    console.error('获取购物车失败:', error); // 网络异常：控制台打印便于排查
    message.error('网络错误，请稍后重试');
  } finally {
    loading.value = false; // 无论成功失败都关闭加载态
  }
};

// 数量变化后重算单行小计：小计 = 单价 × 数量（本地金额同步的辅助函数）
const handleQuantityChange = (record: CartItem) => {
  record.subtotal = record.price * record.quantity;
};

// 移除购物车商品：当前为占位实现，仅提示“功能待实现”，未真正调用删除接口
const handleRemoveItem = async (record: CartItem) => {
  try {
    message.info('移除商品功能待实现');
  } catch (error: any) {
    console.error('移除商品失败:', error);
    message.error('网络错误，请稍后重试');
  }
};

// 点击“去结算”：校验存在可结算商品后，打开确认订单弹窗
//（无可用商品时按钮本身已禁用，这里再做一次兜底校验）
const handleCheckout = () => {
  if (availableItems.value.length === 0) {
    message.warning('购物车内没有可结算的商品');
    return;
  }
  checkoutModalVisible.value = true; // 打开结算确认弹窗
};

const checkoutLoading = ref(false); // 结算请求进行中标志：按钮 loading，防止重复点击提交

// 确认结算：调用 createOrder() 让后端把购物车可结算商品生成订单；
// 成功后关闭弹窗 → 跳转到“我的订单”页 → 重新拉取购物车（已结算条目应从购物车消失）
const handleConfirmCheckout = async () => {
  checkoutLoading.value = true; // 开启按钮 loading，防连点
  try {
    const res = await createOrder(); // 请求后端“购物车结算生成订单”接口
    if (res.data.code === 200) {
      message.success('订单创建成功');
      checkoutModalVisible.value = false; // 关闭结算确认弹窗
      // 跳转到用户个人中心页面
      router.push('/user/profile_order'); // 跳转订单列表页，让用户查看刚生成的订单
      // 刷新购物车数据
      await fetchCart(); // 重新拉取购物车，同步后端结算后的最新数据
    } else {
      message.error(res.data.message || '创建订单失败');
    }
  } catch (error: any) {
    console.error('创建订单失败:', error);
    message.error('网络错误，请稍后重试');
  } finally {
    checkoutLoading.value = false; // 关闭 loading
  }
};

// 点击“修改”：把该行购物车数据回填到 editForm，并打开“修改数量”弹窗
const handleEditItem = (record: CartItem) => {
  editForm.cart_item_id = record.cart_item_id; // 记录条目 ID（保存 / 删除时用于定位）
  editForm.product_name = record.product_name; // 回填商品名称（只读展示）
  editForm.price = record.price;               // 回填单价（只读展示）
  editForm.quantity = record.quantity;         // 回填当前数量（用户可修改）
  editForm.image_url = record.image_url;       // 回填图片路径（弹窗内由 getApiUrl 拼完整地址展示）
  editModalVisible.value = true;               // 打开修改弹窗
};

// 保存数量修改：把 product_id 与新的 quantity 提交给后端 updateCartItem；
// 新数量为 0 → 后端删除该条目，成功后本地列表同步移除；
// 新数量 > 0 → 后端更新成功后本地同步数量与小计
const handleSaveEdit = async () => {
  try {
    // 先在本地列表里按 cart_item_id 找到对应条目（取它的 product_id 作接口参数）
    const item = cartItems.value.find(i => i.cart_item_id === editForm.cart_item_id);
    if (item) {
      // 调用API更新购物车商品数量
      const res = await updateCartItem(item.product_id, editForm.quantity);
      if (res.data.code === 200) {
        if (editForm.quantity === 0) {
          // 如果数量为0，从购物车中移除商品
          const index = cartItems.value.findIndex(i => i.cart_item_id === editForm.cart_item_id);
          if (index !== -1) {
            cartItems.value.splice(index, 1); // 从响应式数组中删除该条目（表格自动刷新）
          }
          message.success('商品从购物车删除成功');
        } else {
          // 更新本地购物车数据
          item.quantity = editForm.quantity;          // 同步数量
          item.subtotal = item.price * item.quantity; // 同步小计，总价计算属性自动跟着更新
          message.success('修改商品数量成功');
        }

      } else {
        message.error(res.data.message || '修改商品数量失败');
      }
    }
  } catch (error: any) {
    console.error('修改商品数量失败:', error);
    message.error('网络错误，请稍后重试', error);
  } finally {
    editModalVisible.value = false; // 无论成败都关闭修改弹窗
  }
};

// 取消修改：仅关闭弹窗，不保存任何改动
const handleCancelEdit = () => {
  editModalVisible.value = false;
};

// “去购物 / 继续购物”：跳转到商品列表页面
const goShopping = () => {
  router.push('/user/products/profile');
};

// 生命周期钩子：页面挂载完成后自动加载一次购物车数据
onMounted(() => {
  fetchCart();
});
</script>

<style scoped>
#profileCartPage {
  min-height: 100vh;
  background: linear-gradient(to left, #21c6fd, #00beff);
  padding: 24px;
}

.cart-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.title {
  margin-bottom: 24px;
  color: #1a1a1a;
  font-size: 22px;
  font-weight: 600;
}

.cart-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.total-price {
  font-size: 18px;
  font-weight: 600;
  color: #ecd960;
}

.unavailable {
  color: #999;
  text-decoration: line-through;
}

.cart-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.checkout-detail {
  padding: 16px 0;
}

.checkout-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.checkout-name {
  flex: 1;
  color: #333;
}

.checkout-qty {
  width: 60px;
  text-align: center;
  color: #666;
}

.checkout-price {
  width: 100px;
  text-align: right;
  color: #333;
  font-weight: 500;
}

.checkout-total {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
  padding-top: 8px;
}

.checkout-total-price {
  font-size: 20px;
  font-weight: 600;
  color: #ff4d4f;
}
</style>
