<template>
  <div id="adminAccountsPage">
    <a-card title="账号管理（用户 / 商家）">
      <!-- 工具栏：类型过滤 + 刷新 -->
      <div class="toolbar">
        <a-space>
          <a-radio-group v-model:value="filters.type" @change="reload">
            <a-radio-button value="all">全部</a-radio-button>
            <a-radio-button value="user">用户</a-radio-button>
            <a-radio-button value="seller">商家</a-radio-button>
          </a-radio-group>
          <a-button @click="reload">刷新</a-button>
        </a-space>
        <span style="margin-left: 16px; color:#888">禁用账号后其旧登录令牌立即失效</span>
      </div>

      <a-table
          :columns="columns"
          :data-source="items"
          :loading="loading"
          row-key="id"
          :pagination="false"
          style="margin-top: 12px"
      >
        <!-- 类型列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <a-tag :color="record.type === 'seller' ? 'orange' : 'blue'">
              {{ record.type === 'seller' ? '商家' : '用户' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'is_active'">
            <a-badge :status="record.is_active ? 'success' : 'error'"
                     :text="record.is_active ? '正常' : '已禁用'"/>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button v-if="record.is_active" size="small" danger @click="toggleActive(record, false)">
                禁用
              </a-button>
              <a-button v-else size="small" type="primary" @click="toggleActive(record, true)">
                启用
              </a-button>
              <a-popconfirm title="确定删除该账号？其名下数据将被级联删除"
                            @confirm="removeAccount(record)">
                <a-button size="small" type="text" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 分页 -->
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
 * [文件级说明] AdminAccountsPage.vue —— 管理员：账号管理页（/admin/accounts）
 * ------------------------------------------------------------------
 * 功能（对应权限矩阵“管理员”行）：
 *   - 查看用户和商家账号列表（全部/用户/商家过滤、分页）；
 *   - 禁用 / 启用账号：后端修改 is_active，被禁账号的旧 token 立即失效；
 *   - 删除账号：后端级联清理其名下数据。
 * 鉴权：路由 meta.roles=['admin'] + 后端 @admin_required 双重保证；
 *       普通用户/审计员访问会被 403 拒绝。
 * 数据：调 adminListAccounts / adminDisableAccount / adminEnableAccount /
 *       adminDeleteAccount（见 src/api/staff.js）。
 */
import {onMounted, reactive, ref} from 'vue';
import {message} from "ant-design-vue";
import {adminListAccounts, adminDisableAccount, adminEnableAccount, adminDeleteAccount} from '@/api/staff';

// 过滤与分页状态
const filters = reactive({type: 'all'});
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const items = ref<any[]>([]);
const loading = ref(false);

// 表格列定义：created_at 等字段由 bodyCell 之外默认渲染
const columns = [
  {title: 'ID', dataIndex: 'id', key: 'id', width: 60},
  {title: '类型', key: 'type', width: 80},
  {title: '用户名', dataIndex: 'username', key: 'username'},
  {title: '角色', dataIndex: 'role', key: 'role', width: 100},
  {title: '状态', key: 'is_active', width: 100},
  {title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 190},
  {title: '操作', key: 'action', width: 160},
];

// 拉取账号列表
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await adminListAccounts({
      type: filters.type,
      page: page.value,
      page_size: pageSize.value,
    });
    if (res.data.code === 0) {
      items.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    } else {
      message.error(res.data.message || '获取列表失败');
    }
  } catch (e) {
    console.error('获取账号列表失败:', e);
  } finally {
    loading.value = false;
  }
};

const reload = () => {
  page.value = 1;
  fetchList();
};
const onPageChange = (p: number, ps: number) => {
  page.value = p;
  pageSize.value = ps;
  fetchList();
};

// 禁用 / 启用
const toggleActive = async (record: any, active: boolean) => {
  try {
    const res = active
        ? await adminEnableAccount(record.type, record.id)
        : await adminDisableAccount(record.type, record.id);
    if (res.data.code === 0) {
      message.success(active ? '已启用' : '已禁用');
      fetchList();
    } else {
      message.error(res.data.message || '操作失败');
    }
  } catch (e) {
    console.error('切换账号状态失败:', e);
  }
};

// 删除账号
const removeAccount = async (record: any) => {
  try {
    const res = await adminDeleteAccount(record.type, record.id);
    if (res.data.code === 0) {
      message.success('删除成功');
      fetchList();
    } else {
      message.error(res.data.message || '删除失败');
    }
  } catch (e) {
    console.error('删除账号失败:', e);
  }
};

onMounted(fetchList);
</script>

<style scoped>
.toolbar {
  margin-bottom: 4px;
}
</style>
