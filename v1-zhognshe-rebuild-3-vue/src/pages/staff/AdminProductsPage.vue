<template>
  <div id="adminProductsPage">
    <a-card title="商品管理（全部商品）">
      <!-- 工具栏：状态过滤 + 名称搜索 + 刷新 -->
      <div class="toolbar">
        <a-space wrap>
          <a-select v-model:value="filters.status" style="width: 130px"
                    placeholder="状态" allow-clear @change="reload">
            <a-select-option value="active">上架中</a-select-option>
            <a-select-option value="inactive">已下架</a-select-option>
          </a-select>
          <a-input v-model:value="filters.keyword" placeholder="按商品名称搜索"
                   style="width: 220px" allow-clear @pressEnter="reload" @change="onKeywordChange"/>
          <a-button type="primary" @click="reload">查询</a-button>
          <a-button @click="resetFilters">重置</a-button>
        </a-space>
      </div>

      <a-table
          :columns="columns"
          :data-source="items"
          :loading="loading"
          row-key="id"
          :pagination="false"
          style="margin-top: 12px"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'red'">
              {{ record.status === 'active' ? '上架中' : '已下架' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'price'">
            ¥{{ (record.price / 100).toFixed(2) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-popconfirm title="确定删除该商品？(管理员操作会写入审计日志)"
                          @confirm="removeProduct(record)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </template>
        </template>
      </a-table>

      <div style="margin-top: 16px; text-align: right">
        <a-pagination
            :current="page"
            :page-size="pageSize"
            :total="total"
            show-size-changer
            @change="onPageChange"
        />
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
/**
 * [文件级说明] AdminProductsPage.vue —— 管理员：商品管理页（/admin/products）
 * ------------------------------------------------------------------
 * 功能（权限矩阵“管理员”行）：
 *   - 查看全站商品列表（状态过滤、按名称搜索、分页）；
 *   - 删除任意商品（不受卖家归属限制，后端为管理员视角删除）。
 * 鉴权：路由 meta.roles=['admin'] + 后端 @admin_required。
 * 说明：价格单位“分”，展示时 /100 转元（与商城各页一致）。
 */
import {onMounted, reactive, ref} from 'vue';
import {message} from "ant-design-vue";
import {adminListProducts, adminDeleteProduct} from '@/api/staff';

const filters = reactive({status: undefined as string | undefined, keyword: ''});
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const items = ref<any[]>([]);
const loading = ref(false);

const columns = [
  {title: 'ID', dataIndex: 'id', key: 'id', width: 60},
  {title: '商品名称', dataIndex: 'name', key: 'name'},
  {title: '价格', key: 'price', width: 110},
  {title: '状态', key: 'status', width: 100},
  {title: '所属商家', dataIndex: 'seller_name', key: 'seller_name', width: 140},
  {title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 190},
  {title: '操作', key: 'action', width: 90},
];

const fetchList = async () => {
  loading.value = true;
  try {
    const res = await adminListProducts({
      page: page.value,
      per_page: pageSize.value,
      status: filters.status,
      name_keyword: filters.keyword || undefined,
    });
    if (res.data.code === 0) {
      items.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    } else {
      message.error(res.data.message || '获取商品列表失败');
    }
  } catch (e) {
    console.error('获取商品列表失败:', e);
  } finally {
    loading.value = false;
  }
};

const reload = () => {
  page.value = 1;
  fetchList();
};
// 输入关键字变化后清空即自动查询
const onKeywordChange = () => {
  if (!filters.keyword) reload();
};
const resetFilters = () => {
  filters.status = undefined;
  filters.keyword = '';
  reload();
};
const onPageChange = (p: number, ps: number) => {
  page.value = p;
  pageSize.value = ps;
  fetchList();
};

const removeProduct = async (record: any) => {
  try {
    const res = await adminDeleteProduct(record.id);
    if (res.data.code === 0) {
      message.success('商品已删除');
      fetchList();
    } else {
      message.error(res.data.message || '删除失败');
    }
  } catch (e) {
    console.error('删除商品失败:', e);
  }
};

onMounted(fetchList);
</script>

<style scoped>
.toolbar {
  margin-bottom: 4px;
}
</style>
