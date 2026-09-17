<template>
  <div id="userProductPage">
    <div class="browse-container">
      <h2 class="title">商品浏览</h2>

      <!-- 搜索栏 -->
      <!-- 支持按商品名称关键字检索、按上/下架状态过滤，便于买家快速定位商品 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="商品名称">
          <a-input
            v-model:value="searchParams.keyword"
            placeholder="请输入关键词"
            allow-clear
            @pressEnter="handleSearch"
          />
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchParams.status"
            placeholder="全部"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="active">上架</a-select-option>
            <a-select-option value="inactive">下架</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>

      <!-- 商品表格 -->
      <!-- 数据由后端分页返回，翻页/改每页条数经 @change 重新请求；行内“查看详情”打开详情弹窗 -->
      <a-table
        :columns="columns"
        :data-source="productList"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        bordered
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'image_url'">
            <!-- 图片列：image_url 为相对路径，用 getApiUrl() 拼接完整地址展示缩略图，无图则显示“无照片” -->
            <template v-if="record.image_url">
              <img :src="getApiUrl(record.image_url)" style="width: 60px; height: 60px; object-fit: cover" />
            </template>
            <template v-else>
              <span>无照片</span>
            </template>
          </template>
          <template v-if="column.key === 'price'">
            <!-- 价格列：price 单位为“分”，除以 100 转成“元”并保留两位小数 -->
            {{ (record.price / 100).toFixed(2) }} 元
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '上架' : '下架' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <!-- 操作列：查看该商品完整详情（先回填到 currentProduct 再弹出详情对话框） -->
            <a-button type="link" size="small" @click="handleViewDetail(record)">查看详情</a-button>
          </template>
        </template>
      </a-table>

      <!-- 商品详情弹窗 -->
      <!-- 集中展示买家关注的商品信息，支持选择数量加入购物车（仅上架商品可点击“加入购物车”） -->
      <a-modal
        v-model:open="detailModalVisible"
        title="商品详情"
        width="800px"
        @cancel="handleCancelDetail"
      >
        <div class="product-detail">
          <div class="detail-row">
            <span class="detail-label">商品照片：</span>
            <span class="detail-value">
              <!-- 详情大图：同样是相对路径，经 getApiUrl() 拼接后展示 -->
              <template v-if="currentProduct.image_url">
                <img :src="getApiUrl(currentProduct.image_url)" style="width: 200px; height: 200px; object-fit: cover" />
              </template>
              <template v-else>
                <span>无照片</span>
              </template>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">商品名称：</span>
            <span class="detail-value">{{ currentProduct.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">商品价格：</span>
            <span class="detail-value">{{ (currentProduct.price / 100).toFixed(2) }} 元</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">商品描述：</span>
            <span class="detail-value">{{ currentProduct.description || '无描述' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">商品状态：</span>
            <span class="detail-value">
              <a-tag :color="currentProduct.status === 'active' ? 'green' : 'default'">
                {{ currentProduct.status === 'active' ? '上架' : '下架' }}
              </a-tag>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">商家名称：</span>
            <span class="detail-value">{{ currentProduct.seller_name || '未知商家' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">上架时间：</span>
            <span class="detail-value">{{ currentProduct.created_at }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">购买数量：</span>
            <span class="detail-value">
              <a-input-number v-model:value="cartQuantity" :min="1" :max="99" style="width: 100px" />
            </span>
          </div>
        </div>
        <template #footer>
          <div class="modal-footer">
            <a-button @click="handleCancelDetail">取消</a-button>
            <a-button type="primary" @click="handleAddToCart" :disabled="currentProduct.status !== 'active'">
              加入购物车
            </a-button>
          </div>
        </template>
      </a-modal>
    </div>
  </div>
</template>

<script lang="ts" setup>
// ============================================================
// 页面级注释：UserProductBrowsePage.vue —— 买家“浏览商品”页面
// 功能：分页展示全部商品，支持按“商品名称关键字 + 上/下架状态”组合过滤；
//       点击行内“查看详情”弹出详情对话框（大图、价格、描述、状态、商家、上架时间），
//       买家可选择购买数量并“加入购物车”（商品非上架状态时按钮置灰，不可加购）。
// 关键设计：
//  1) 服务端分页 + 过滤：把 page / size / keyword / status 组装成查询参数交给
//     getUserProducts 接口，后端返回当前页 items 与总条数 total 驱动分页器；
//  2) 价格展示：后端以“分”存储，前端用 (price / 100).toFixed(2) 显示为“元”；
//  3) 图片展示：image_url 为相对路径，统一经 getApiUrl() 拼接成完整 URL 后渲染；
//  4) 加入购物车：调用 addToCart(商品id, 购买数量) 接口，该接口约定的业务成功码
//     是 200（与列表接口的 0 不同）；成功后关闭弹窗并把购买数量重置为 1。
// ============================================================
import { reactive, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
// 后端接口：getUserProducts 分页/过滤查询商品列表，addToCart 加入购物车；
// getApiUrl 用于把相对图片路径拼成完整 URL
import { getUserProducts, addToCart } from '@/api/product';
import { getApiUrl } from '@/request';

// 商品数据结构：与后端返回字段一致（price 单位为“分”，seller_name 为商家名称，image_url 为相对路径）
interface ProductItem {
  id: number;
  name: string;
  price: number;
  description: string;
  status: 'active' | 'inactive';
  seller_id: number;
  seller_name: string;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

// 列表加载状态：请求期间表格显示 loading 效果
const loading = ref(false);
// 当前页商品列表（由 getUserProducts 返回的 items 填充）
const productList = ref<ProductItem[]>([]);

// 详情弹窗相关变量
const detailModalVisible = ref(false);
const cartQuantity = ref(1); // 购物车数量，默认值为1
const currentProduct = reactive({
  id: 0,
  name: '',
  price: 0,
  description: '',
  status: 'active' as 'active' | 'inactive',
  seller_id: 0,
  seller_name: '',
  image_url: null as string | null,
  created_at: '',
  updated_at: ''
});

// 搜索参数
// 搜索过滤条件：keyword 按商品名称检索；status 限定上/下架，不选表示不过滤
const searchParams = reactive({
  keyword: '',
  status: undefined as string | undefined,
});

// 分页配置
// 分页状态：current 当前页码、pageSize 每页条数（默认 12）、total 总条数（后端回填）；
// 其余为 antd 分页器 UI 配置，showTotal 显示“共 N 条商品”
const pagination = reactive({
  current: 1,
  pageSize: 12,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条商品`,
});

// 表格列定义
const columns = [
  { 
    title: '商品照片', 
    dataIndex: 'image_url', 
    key: 'image_url', 
    width: 100,
  },
  { title: '商品名称', dataIndex: 'name', key: 'name' },
  { title: '价格', key: 'price', width: 150 },
  { title: '状态', key: 'status', width: 100 },
  { title: '上架时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 120 },
];

// 获取商品列表
const fetchProducts = async () => {
  loading.value = true;
  try {
    // 组装查询参数：page/size 控制分页；keyword、status 未选择时传 undefined 表示不过滤
    const res = await getUserProducts({
      page: pagination.current,
      size: pagination.pageSize,
      keyword: searchParams.keyword || undefined,
      status: searchParams.status || undefined,
    });
    if (res.data.code === 0) {
      // 后端统一响应 code===0 为成功；data.items 为当前页商品，data.total 为总条数
      const data = res.data.data;
      productList.value = data.items || [];
      pagination.total = data.total || 0;
    } else {
      message.error(res.data.message || '获取商品列表失败');
    }
  } catch (error: any) {
    console.error('获取商品列表失败:', error);
    message.error('网络错误，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 搜索
// 搜索回调（点“搜索”按钮或输入框回车触发）：条件变化后页码重置为 1 再重新查询
const handleSearch = () => {
  pagination.current = 1;
  fetchProducts();
};

// 重置搜索条件
// 重置回调：清空关键字与状态条件并回到第 1 页，恢复展示全部商品
const handleReset = () => {
  searchParams.keyword = '';
  searchParams.status = undefined;
  pagination.current = 1;
  fetchProducts();
};

// 表格变化
// 表格变化回调：翻页 / 切换每页条数后同步分页参数，再向后端请求对应页数据
const handleTableChange = (pag: any) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchProducts();
};

// 查看详情
const handleViewDetail = (record: ProductItem) => {
  // 填充商品信息
  currentProduct.id = record.id;
  currentProduct.name = record.name;
  currentProduct.price = record.price;
  currentProduct.description = record.description;
  currentProduct.status = record.status;
  currentProduct.seller_id = record.seller_id;
  currentProduct.seller_name = record.seller_name;
  currentProduct.image_url = record.image_url;
  currentProduct.created_at = record.created_at;
  currentProduct.updated_at = record.updated_at;
  // 打开详情弹窗
  detailModalVisible.value = true;
};

// 取消查看详情
const handleCancelDetail = () => {
  detailModalVisible.value = false;
};

// 加入购物车
const handleAddToCart = async () => {
  try {
    // 调用后端加入购物车接口：传入商品 id 与所选购买数量
    const res = await addToCart(currentProduct.id, cartQuantity.value);
    // 注意：加入购物车接口的业务成功码约定为 200（与列表接口的 0 不同，此处按后端约定判断）
    if (res.data.code === 200) {
      message.success('加入购物车成功');
      detailModalVisible.value = false;
      // 重置数量为默认值
      cartQuantity.value = 1;
    } else {
      message.error(res.data.message || '加入购物车失败');
    }
  } catch (error: any) {
    console.error('加入购物车失败:', error);
    message.error('网络错误，请稍后重试');
  }
};

// 组件挂载完成后自动加载第 1 页商品
onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
#userProductPage {
  min-height: 100vh;
  background: linear-gradient(to left, #21c6fd, #00beff);
  padding: 24px;
}

.browse-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.title {
  margin-bottom: 24px;
  color: #1a1a1a;
  font-size: 22px;
  font-weight: 600;
}

.search-form {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
}

/* 商品详情弹窗样式 */
.product-detail {
  padding: 16px 0;
}

.detail-row {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}

.detail-label {
  width: 100px;
  font-weight: 600;
  color: #333;
}

.detail-value {
  flex: 1;
  color: #666;
  word-break: break-word;
}
</style>
