<template>
  <div id="sellerProductPage">
    <div class="manage-container">
      <div class="header">
        <h2 class="title">我的商品</h2>
        <a-button type="primary" @click="router.push('/product/create')">新建商品</a-button>
      </div>

      <!-- 搜索栏 -->
      <!-- 按商品名称关键字检索、按上/下架状态过滤；“重置”清空条件恢复全部商品 -->
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
      <!-- 数据由后端分页返回，分页器变化经 @change 触发 handleTableChange 重新请求列表 -->
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
            <!-- 图片列：后端返回相对路径 image_url，需用 getApiUrl() 拼成完整地址才能显示 -->
            <template v-if="record.image_url">
              <img :src="getApiUrl(record.image_url)" style="width: 60px; height: 60px; object-fit: cover" />
            </template>
            <template v-else>
              <span>无照片</span>
            </template>
          </template>
          <template v-if="column.key === 'price'">
            <!-- 价格列：price 单位为“分”，这里除以 100 转成“元”并保留两位小数展示 -->
            {{ (record.price / 100).toFixed(2) }} 元
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '上架' : '下架' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <!-- 操作列：编辑→handleEdit 打开弹窗并回填数据；删除→a-popconfirm 二次确认后执行 handleDelete -->
            <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-popconfirm
              title="确定要删除该商品吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="handleDelete(record.id)"
            >
              <a-button type="link" size="small" danger>删除</a-button>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 编辑商品对话框 -->
    <!-- 弹窗表单保存时调用 handleSaveEdit：价格“元”转“分”，状态可切上下架，成功后关闭弹窗并刷新列表 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑商品"
      @ok="handleSaveEdit"
      @cancel="handleCancelEdit"
    >
      <a-form
        :model="editForm"
        layout="vertical"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="商品名称">
          <a-input v-model:value="editForm.name" placeholder="请输入商品名称" />
        </a-form-item>
        <a-form-item label="商品描述">
          <a-textarea v-model:value="editForm.description" placeholder="请输入商品描述" :rows="4" />
        </a-form-item>
        <a-form-item label="商品价格">
          <a-input-number
            v-model:value="editForm.price"
            :min="0"
            :step="0.01"
            placeholder="请输入商品价格"
          />
        </a-form-item>
        <a-form-item label="商品照片">
          <a-upload
            v-model:file-list="editFileList"
            :max-count="1"
            :show-upload-list="true"
            :before-upload="beforeUpload"
            :on-remove="onEditRemove"
            :custom-request="customEditRequest"
            accept="image/*"
          >
            <a-button>
              <upload-outlined></upload-outlined>
              上传照片
            </a-button>
          </a-upload>
          <div class="field-tip">支持 JPG、PNG 格式，每个商品最多上传 1 张照片</div>
        </a-form-item>
        <a-form-item label="商品状态">
          <a-select v-model:value="editForm.status" placeholder="请选择商品状态">
            <a-select-option value="active">上架</a-select-option>
            <a-select-option value="inactive">下架</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
// ============================================================
// 页面级注释：SellerProductManagePage.vue —— 商家“我的商品”管理页面
// 功能：分页展示当前商家发布的商品，支持按“商品名称关键字 + 上架/下架状态”组合
//       过滤搜索；列表内可删除商品（删除前 a-popconfirm 二次确认），点击“编辑”会
//       弹出对话框修改商品信息（名称/描述/价格/照片/状态，把状态改为 inactive 即
//       相当于下架），页头“新建商品”按钮可跳转到发布页面。
// 关键设计：
//  1) 服务端分页 + 过滤：把 page / size / keyword / status 组装成查询参数交给
//     getSellerProducts 接口，后端返回当前页 items 与总条数 total，前端把 total
//     回填给分页器并展示“共 N 条”；
//  2) 价格以“分”存储：表格展示除以 100 转“元”；编辑弹窗输入“元”，保存时乘 100
//     转回“分”（均用 Math.round 规避浮点误差）；
//  3) 商品图片 image_url 为相对路径，模板中必须用 getApiUrl() 拼成完整地址才能显示；
//  4) 删除成功后若当前页被删空且不在第 1 页，自动回退一页再刷新，避免出现空页。
// ============================================================
import { reactive, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { UploadOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';
// 后端接口：getSellerProducts 查询自己的商品、deleteProduct 删除、updateProduct 更新；
// getApiUrl 用于把后端返回的相对图片路径拼成完整 URL
import { getSellerProducts, deleteProduct, updateProduct } from '@/api/product';
import { getApiUrl } from '@/request';

const router = useRouter();

// 商品数据结构：与后端列表接口返回的单条商品对应（price 单位为“分”，image_url 为相对路径）
interface ProductItem {
  id: number;
  name: string;
  price: number;
  description: string;
  status: 'active' | 'inactive';
  seller_id: number;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

// 列表加载状态：请求期间表格显示 loading 效果
const loading = ref(false);
// 当前页商品列表数据（由后端返回的 items 填充，作为表格数据源）
const productList = ref<ProductItem[]>([]);

// 编辑相关变量
const editModalVisible = ref(false);
const currentProductId = ref(0);
const editForm = reactive({
  name: '',
  description: '',
  price: 0,
  status: 'active' as 'active' | 'inactive',
});

// 编辑文件相关变量
const editFileList = ref([]);
const editUploadedFile = ref(null);

// 文件上传前验证
const beforeUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('只能上传 JPG/PNG 格式的图片！');
    return false;
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB！');
    return false;
  }
  return true;
};

// 编辑时文件移除时的处理
const onEditRemove = (file) => {
  editUploadedFile.value = null;
  editFileList.value = [];
};

// 编辑时自定义上传逻辑
const customEditRequest = (options) => {
  const { file, onSuccess, onError } = options;
  editUploadedFile.value = file;
  // 模拟上传成功
  setTimeout(() => {
    onSuccess?.(file);
  }, 1000);
};

// 搜索参数
// 搜索过滤条件：keyword 为商品名称关键字；status 限定上架(active)/下架(inactive)，不选表示全部
const searchParams = reactive({
  keyword: '',
  status: undefined as string | undefined,
});

// 分页配置
// 分页状态：current 当前页码、pageSize 每页条数、total 总条数（后端返回后回填）；
// 其余为 antd 分页器 UI 配置（可切换每页条数、快速跳页、显示“共 N 条”）
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`,
});

// 表格列定义
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { 
    title: '商品照片', 
    dataIndex: 'image_url', 
    key: 'image_url', 
    width: 100,
  },
  { title: '商品名称', dataIndex: 'name', key: 'name' },
  { title: '价格', key: 'price', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 150 },
];

// 获取商品列表
const fetchProducts = async () => {
  loading.value = true;
  try {
    // 组装查询参数：page/size 控制分页；keyword、status 为空时传 undefined（后端视为不过滤）
    const res = await getSellerProducts({
      page: pagination.current,
      size: pagination.pageSize,
      keyword: searchParams.keyword || undefined,
      status: searchParams.status,
    });
    if (res.data.code === 0) {
      // 后端统一响应 code===0 表示成功；data.items 为当前页记录，data.total 为符合条件总条数
      const data = res.data.data;
      productList.value = data.items || [];
      pagination.total = data.total || 0;
      // 打印商品数据，检查 image_url 字段
      console.log('商品列表数据:', data.items);
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
// 搜索回调（点“搜索”按钮或输入框回车触发）：条件变化后回到第 1 页再重新查询
const handleSearch = () => {
  pagination.current = 1;
  fetchProducts();
};

// 重置搜索条件
// 重置回调：清空关键字与状态筛选、回到第 1 页，恢复显示全部商品
const handleReset = () => {
  searchParams.keyword = '';
  searchParams.status = undefined;
  pagination.current = 1;
  fetchProducts();
};

// 表格变化（分页、排序等）
// 表格变化回调：antd 翻页或切换每页条数时触发，同步分页参数后重新请求服务端数据
const handleTableChange = (pag: any) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchProducts();
};

// 编辑商品
const handleEdit = (record: ProductItem) => {
  currentProductId.value = record.id;
  editForm.name = record.name;
  editForm.description = record.description;
  editForm.price = record.price / 100; // 转换为元
  editForm.status = record.status;
  editModalVisible.value = true;
};

// 保存编辑
const handleSaveEdit = async () => {
  try {
    // 创建 FormData 对象
    const formData = new FormData();
    formData.append('name', editForm.name);
    formData.append('description', editForm.description);
    formData.append('price', Math.round(editForm.price * 100).toString()); // 转换为分
    formData.append('status', editForm.status);

    // 如果有上传的文件，添加到 FormData
    if (editUploadedFile.value) {
      formData.append('image', editUploadedFile.value);
    }

    // 调用后端更新商品接口（按商品 id），请求体同样是 FormData（含可能新上传的图片）
    const res = await updateProduct(currentProductId.value, formData);
    if (res.data.code === 0) {
      message.success('编辑成功');
      editModalVisible.value = false;
      // 重置文件列表
      editFileList.value = [];
      editUploadedFile.value = null;
      fetchProducts();
    } else {
      message.error(res.data.message || '编辑失败');
    }
  } catch (error: any) {
    console.error('编辑失败:', error);
    message.error('编辑失败，请稍后重试');
  }
};

// 取消编辑
const handleCancelEdit = () => {
  editModalVisible.value = false;
  // 重置文件列表
  editFileList.value = [];
  editUploadedFile.value = null;
};

// 删除商品
const handleDelete = async (id: number) => {
  try {
    // 调用后端删除商品接口（删除前已由 a-popconfirm 弹窗二次确认）
    const res = await deleteProduct(id);
    if (res.data.code === 0) {
      message.success('删除成功');
      // 如果当前页只剩一条数据且不是第一页，则回到上一页
      if (productList.value.length === 1 && pagination.current > 1) {
        pagination.current--;
      }
      fetchProducts();
    } else {
      message.error(res.data.message || '删除失败');
    }
  } catch (error: any) {
    console.error('删除失败:', error);
    message.error('删除失败，请稍后重试');
  }
};

// 组件挂载完成后自动加载第 1 页商品数据
onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
#sellerProductPage {
  min-height: 100vh;
  background: linear-gradient(to left, #21c6fd, #00beff);
  padding: 24px;
}

.manage-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  margin: 0;
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

:deep(.ant-table) {
  font-size: 14px;
}
</style>
