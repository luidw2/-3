<template>
  <div id="auditLogPage">
    <a-card title="审计日志（只读）">
      <!-- 过滤区：事件类型 + 时间范围 + 导出 -->
      <div class="toolbar">
        <a-space wrap>
          <a-input v-model:value="filters.event_type" placeholder="事件类型，如 STAFF_LOGIN_OK"
                   style="width: 240px" allow-clear @pressEnter="reload"/>
          <span>开始</span>
          <input type="date" v-model="filters.start" class="date-input"/>
          <span>结束</span>
          <input type="date" v-model="filters.end" class="date-input"/>
          <a-button type="primary" @click="reload">查询</a-button>
          <a-button @click="handleExport" :loading="exporting">导出 CSV</a-button>
        </a-space>
        <div style="color:#888; font-size:12px; margin-top:8px">
          审计员只读日志与安全事件；查看与导出行为本身也会被记录（AUDITOR_EXPORT）。
        </div>
      </div>

      <a-table
          :columns="columns"
          :data-source="events"
          :loading="loading"
          row-key="id"
          :pagination="false"
          size="middle"
          style="margin-top: 12px"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'event_type'">
            <a-tag>{{ record.event_type }}</a-tag>
          </template>
          <template v-else-if="column.key === 'details'">
            <span :title="record.details" style="display:inline-block; max-width: 420px;
                  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; vertical-align:bottom;">
              {{ record.details }}
            </span>
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
 * [文件级说明] AuditLogPage.vue —— 审计员：审计日志页（/auditor/logs）
 * ------------------------------------------------------------------
 * 功能（权限矩阵“审计员”行，只读）：
 *   - 分页查看安全审计日志 / 安全事件，可按事件类型与起止日期过滤；
 *   - 导出 CSV：调 auditorExport（blob 响应）后用浏览器下载；
 *   - 不能管理用户、修改商品、处理订单 —— 路由 meta.roles=['auditor'] +
 *     后端 @auditor_required 双重限制，越权一律 403。
 */
import {onMounted, reactive, ref} from 'vue';
import {message} from "ant-design-vue";
import {auditorListEvents, auditorExport} from '@/api/staff';

const filters = reactive({event_type: '', start: '', end: ''});
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);
const events = ref<any[]>([]);
const loading = ref(false);
const exporting = ref(false);

const columns = [
  {title: 'ID', dataIndex: 'id', key: 'id', width: 70},
  {title: '事件类型', key: 'event_type', width: 190},
  {title: '操作账号', dataIndex: 'username', key: 'username', width: 140},
  {title: '详情', key: 'details'},
  {title: '时间', dataIndex: 'created_at', key: 'created_at', width: 190},
];

const fetchList = async () => {
  loading.value = true;
  try {
    const res = await auditorListEvents({
      page: page.value,
      page_size: pageSize.value,
      event_type: filters.event_type || undefined,
      start: filters.start || undefined,
      end: filters.end || undefined,
    });
    if (res.data.code === 0) {
      events.value = res.data.data.events || [];
      total.value = res.data.data.total || 0;
    } else {
      message.error(res.data.message || '获取日志失败');
    }
  } catch (e) {
    console.error('获取审计日志失败:', e);
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

// 导出 CSV：后端返回 blob，用对象 URL 触发浏览器下载
const handleExport = async () => {
  exporting.value = true;
  try {
    const res = await auditorExport({
      event_type: filters.event_type || undefined,
      start: filters.start || undefined,
      end: filters.end || undefined,
    });
    const blob = new Blob([res.data], {type: 'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_events_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    message.success('审计日志已导出');
  } catch (e) {
    console.error('导出失败:', e);
    message.error('导出失败');
  } finally {
    exporting.value = false;
  }
};

onMounted(fetchList);
</script>

<style scoped>
.toolbar {
  margin-bottom: 4px;
}
.date-input {
  width: 150px;
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
}
</style>
