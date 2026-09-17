<template>
  <div id="profileOrderPage">
    <div class="order-container">
      <h2 class="title">我的订单</h2>

      <!-- 订单列表 -->
      <a-table
        :columns="columns"
        :data-source="orders"
        :loading="loading"
        row-key="order_id"
        bordered
        :pagination="{
          current: page,
          pageSize: pageSize,
          total: total,
          onChange: handlePageChange
        }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'total_price'">
            {{ (record.total_price / 100).toFixed(2) }} 元
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template v-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleViewDetail(record.order_id)">详情</a-button>
          </template>
        </template>
      </a-table>

      <!-- 订单详情弹窗 -->
      <a-modal
        v-model:open="detailModalVisible"
        title="订单详情"
        :width="800"
        :maskClosable="true"
        :footer="null"
      >
        <!-- 订单详情主体：orderDetail 有数据才渲染；请求中 / 无数据时走下方 else 显示加载中 -->
        <div v-if="orderDetail" class="order-detail">
          <div class="detail-header">
            <div class="detail-info">
              <span class="order-id">订单号：{{ orderDetail.order_id }}</span>
              <span class="order-status">
                状态：<a-tag :color="getStatusColor(orderDetail.status)">{{ getStatusText(orderDetail.status) }}</a-tag>
              </span>
              <span class="order-time">创建时间：{{ formatDate(orderDetail.created_at) }}</span>
            </div>
          </div>
          
          <a-divider />
          
          <div class="detail-items">
            <h3>商品信息</h3>
            <a-table
              :columns="detailColumns"
              :data-source="orderDetail.items"
              row-key="product_id"
              :pagination="false"
              bordered
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
                <template v-if="column.key === 'price'">
                  {{ (record.price / 100).toFixed(2) }} 元
                </template>
                <template v-if="column.key === 'subtotal'">
                  {{ (record.subtotal / 100).toFixed(2) }} 元
                </template>
              </template>
            </a-table>
          </div>
          
          <a-divider />
          
          <div class="detail-footer">
            <div class="total-price">
              <span>订单总价：</span>
              <span class="price">{{ (orderDetail.total_price / 100).toFixed(2) }} 元</span>
            </div>
            <!-- 支付操作区：仅“待支付(pending)”订单显示“确认支付”按钮，点击走模拟支付流程 -->
            <div class="footer-actions">
              <a-button 
                v-if="orderDetail.status === 'pending'"
                type="primary" 
                size="large" 
                @click="handlePay(orderDetail.order_id)"
              >
                确认支付
              </a-button>
            </div>
          </div>
        </div>
        <div v-else class="loading-detail">
          <a-spin tip="加载中..." />
        </div>
      </a-modal>
    </div>
  </div>
</template>

<script lang="ts" setup>
// ============================================================
// 页面：订单中心（ProfileOrder.vue）
// 讲解要点：
//   1. 数据流：进入页面 onMounted → fetchOrders() 分页拉取订单列表；
//      点“详情”→ 打开弹窗并调 getOrderDetail() 拉取该订单明细；
//      点“确认支付”→ 调 preparePayment() 获取支付链接 → 跳转模拟银行收银台。
//   2. 模拟支付流程：后端 /api/pay/prepare（前端封装 preparePayment）会返回
//      pay_url，前端收到后延时 100ms 执行 window.location.href = pay_url，
//      整页跳转到“模拟银行”页面完成支付，返回后本页刷新即可看到新状态。
//   3. 状态展示：status 字段经 getStatusColor / getStatusText 映射为中文文案
//      “待支付 / 已支付 / 已发货 / 已完成 / 已取消”及对应颜色的标签。
//   4. 金额单位：total_price、subtotal 等金额以“分”存储，展示时 /100 转“元”。
// ============================================================
import { ref, onMounted } from 'vue';    // Vue 组合式 API：ref 声明响应式数据，onMounted 挂载钩子
import { message } from 'ant-design-vue'; // Ant Design Vue 消息提示（loading / 错误提示）
import { getUserOrders, getOrderDetail, preparePayment } from '@/api/product'; // 订单列表 / 订单详情 / 支付准备 三个后端接口封装
import { getApiUrl } from '@/request';   // 把后端返回的相对图片路径拼接成完整可访问 URL

// 订单列表项的数据结构（表格一行对应一个订单）
interface Order {
  order_id: number;    // 订单号
  total_price: number; // 订单总金额（单位：分，展示时 /100 转元）
  status: string;      // 订单状态码：pending / paid / shipped / completed / cancelled
  item_count: number;  // 商品总件数
  created_at: string;  // 下单时间
}

// 订单详情的数据结构：在列表项基础上多出 user_id 与商品明细数组 items
interface OrderDetail {
  order_id: number;
  user_id: number;
  total_price: number;
  status: string;
  created_at: string;
  items: Array<{       // 订单内商品明细（弹窗中嵌套表格逐行展示）
    id: number;
    product_id: number;    // 商品 ID（作为嵌套表格行 key）
    product_name: string;  // 商品名称
    price: number;         // 成交单价（单位：分）
    quantity: number;      // 购买数量
    subtotal: number;      // 小计 = 单价 × 数量（单位：分）
    image_url: string | null; // 商品图片相对路径，为空时显示“无照片”
    created_at: string;
  }>;
}

// —— 订单列表分页状态 ——
const loading = ref(false);          // 列表加载中标志（驱动表格 loading）
const orders = ref<Order[]>([]);     // 订单列表数据（仅当前页，由后端按页返回）
const total = ref(0);                // 订单总条数（后端返回，用于分页组件显示总览）
const page = ref(1);                 // 当前页码
const pageSize = ref(10);            // 每页条数

// —— 订单详情弹窗状态 ——
const detailModalVisible = ref(false);               // 详情弹窗是否显示
const orderDetail = ref<OrderDetail | null>(null);   // 当前查看的订单详情（null 时弹窗内显示“加载中”）
const detailLoading = ref(false);                    // 详情请求进行中标志

// 订单列表表格列配置（金额 / 状态 / 时间等列在 bodyCell 中自定义渲染）
const columns = [
  { title: '订单号', dataIndex: 'order_id', key: 'order_id' },
  { title: '商品数量', dataIndex: 'item_count', key: 'item_count' },
  { title: '订单总价', key: 'total_price', width: 120 }, // 单元格按“xx 元”格式展示
  { title: '订单状态', key: 'status', width: 120 },      // 单元格按状态渲染彩色标签
  { title: '创建时间', key: 'created_at', width: 180 },  // 单元格用 formatDate 格式化时间
  { title: '操作', key: 'action', width: 100 },          // 单元格渲染“详情”按钮
];

// 详情弹窗内“商品明细”嵌套表格的列配置
const detailColumns = [
  { title: '商品照片', dataIndex: 'image_url', key: 'image_url', width: 100 },
  { title: '商品名称', dataIndex: 'product_name', key: 'product_name', width: 250 },
  { title: '单价', key: 'price', width: 100 },       // 单元格按“xx 元”格式展示
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80 },
  { title: '小计', key: 'subtotal', width: 100 },    // 单元格按“xx 元”格式展示
];

// 拉取订单列表：携带分页参数（当前页 page / 每页条数 pageSize）请求 getUserOrders，
// 成功后把“当前页订单列表”写入 orders、“总条数”写入 total 驱动分页器
const fetchOrders = async () => {
  loading.value = true; // 开启列表加载态
  try {
    const res = await getUserOrders({ page: page.value, page_size: pageSize.value });
    if (res.data.code === 200) {
      orders.value = res.data.data.orders || []; // 当前页订单列表
      total.value = res.data.data.total || 0;    // 订单总条数（分页器显示总数）
    } else {
      message.error(res.data.message || '获取订单列表失败');
    }
  } catch (error: any) {
    console.error('获取订单列表失败:', error);
    message.error('网络错误，请稍后重试');
  } finally {
    loading.value = false; // 关闭加载态
  }
};

// 分页切换：更新当前页码后重新请求对应页的订单数据
const handlePageChange = (pageNum: number) => {
  page.value = pageNum;
  fetchOrders(); // 页码变化即重新拉取
};

// 查看订单详情：先打开弹窗（此时可能仍在加载），再调 getOrderDetail 拉取明细；
// 成功则缓存进 orderDetail 渲染；失败 / 网络异常则关闭弹窗并提示
const handleViewDetail = async (orderId: number) => {
  detailLoading.value = true;      // 详情加载中
  detailModalVisible.value = true; // 打开详情弹窗（数据未返回前展示“加载中”）
  try {
    const res = await getOrderDetail(orderId);
    if (res.data.code === 200) {
      orderDetail.value = res.data.data; // 成功：缓存订单详情，弹窗渲染商品明细与金额
    } else {
      message.error(res.data.message || '获取订单详情失败');
      detailModalVisible.value = false; // 业务失败：关闭弹窗
    }
  } catch (error: any) {
    console.error('获取订单详情失败:', error);
    message.error('网络错误，请稍后重试');
    detailModalVisible.value = false; // 网络异常：同样关闭弹窗
  } finally {
    detailLoading.value = false; // 结束加载态
  }
};


// 发起“模拟支付”：调 preparePayment（对应后端 /api/pay/prepare）拿到支付跳转地址
// pay_url，再通过 window.location.href 整页跳转到“模拟银行”页面完成支付
const handlePay = async (orderId: number) => {
  const confirmLoading = message.loading('正在准备支付...', 0); // 弹 loading 提示；第二参 0 表示不自动关闭，返回值是关闭函数
  try {
    const res = await preparePayment(orderId); // 请求后端准备支付，生成模拟支付链接
    if (res.data.code === 200) {
      const payUrl = res.data.data.pay_url; // 取出支付跳转地址（模拟银行收银台 URL）

      // 强制输出
      //console.log('【支付链接】', payUrl);
      //alert('确认跳转链接：\n' + payUrl);

      // 延迟一下再跳转，避免 alert 没消失就被跳转
      setTimeout(() => {
        window.location.href = payUrl; // 整页跳转到模拟银行页面（支付完成后会跳回本系统）
      }, 100);
    } else {
      message.error(res.data.message || '支付准备失败');
    }
  } catch (error: any) {
    console.error('支付准备失败:', error);
    message.error('网络错误，请稍后重试');
  } finally {
    confirmLoading(); // 调用 message.loading 返回的关闭函数，收起“正在准备支付”提示
  }
};


// 订单状态码 → 标签颜色映射：待支付蓝 / 已支付绿 / 已发货橙 / 已完成紫 / 已取消红
const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    pending: 'blue',
    paid: 'green',
    shipped: 'orange',
    completed: 'purple',
    cancelled: 'red'
  };
  return colorMap[status] || 'default'; // 未知状态回退为默认颜色
};

// 订单状态码 → 中文文案映射（列表与详情中的状态标签统一使用）
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待支付',
    paid: '已支付',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  };
  return textMap[status] || status; // 未知状态直接展示原始状态码
};

// 时间格式化：把后端返回的时间字符串转为浏览器本地 zh-CN 可读格式
const formatDate = (dateString: string) => {
  if (!dateString) return ''; // 空值直接返回空串，避免 new Date('') 产生无效时间
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 生命周期钩子：页面挂载完成后自动加载第一页订单
onMounted(() => {
  fetchOrders();
});
</script>

<style scoped>
#profileOrderPage {
  min-height: 100vh;
  background: linear-gradient(to left, #21c6fd, #00beff);
  padding: 24px;
}

.order-container {
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

.order-detail {
  padding: 16px 0;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.order-id {
  font-weight: 600;
  color: #333;
}

.order-status {
  margin-left: 16px;
}

.order-time {
  margin-left: 16px;
  color: #666;
}

.detail-items {
  margin: 24px 0;
}

.detail-items h3 {
  margin-bottom: 16px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.detail-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-price {
  font-size: 18px;
  font-weight: 600;
}

.footer-actions {
  margin-top: 16px;
}

.price {
  color: #ff4d4f;
  margin-left: 8px;
}

.loading-detail {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
