<template>
  <!-- ============================================================
       后台登录页（路由 /staff/login）
       管理员/审计员的登录入口：两步认证流程
       ============================================================ -->
  <div id="staffLoginPage">
    <div class="staff-card">
      <h2 class="staff-title">后台管理系统登录</h2>

      <!-- —— 第一步：用户名 + 密码 —— -->
      <a-form
          v-if="step === 'password'"
          :model="formState"
          label-align="left"
          :label-col="{ span: 4 }"
          :wrapper-col="{ span: 20 }"
          autocomplete="off"
          @finish="handlePasswordLogin"
      >
        <a-form-item label="账号" name="username"
                     :rules="[{ required: true, message: '请输入账号' }]">
          <a-input v-model:value="formState.username" placeholder="请输入后台账号（admin1 / audit1）"/>
        </a-form-item>
        <a-form-item label="密码" name="password"
                     :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="formState.password" placeholder="请输入密码"/>
        </a-form-item>
        <a-form-item :wrapper-col="{ offset: 8, span: 12 }">
          <a-button type="primary" html-type="submit" :loading="submitting">下一步</a-button>
        </a-form-item>
      </a-form>

      <!-- —— 第二步：TOTP 动态码 / 恢复码 —— -->
      <a-form
          v-else-if="step === 'totp'"
          :model="formState"
          label-align="left"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 18 }"
          @finish="handleTotpLogin"
      >
        <a-alert type="info" show-icon style="margin-bottom: 16px"
                 :message="`账号 ${formState.username} 已绑定 TOTP，请输入认证器中的 6 位动态码`"/>
        <a-form-item label="动态码" name="totpCode"
                     :rules="[{ required: true, pattern: /^\d{6}$/, message: '请输入6位数字动态码' }]">
          <a-input v-model:value="formState.totpCode" maxlength="6" placeholder="6位动态码"/>
        </a-form-item>
        <a-form-item :wrapper-col="{ offset: 6, span: 18 }">
          <a-button type="primary" html-type="submit" :loading="submitting">登录</a-button>
          <a-button style="margin-left: 8px" @click="step = 'recovery'">使用恢复码</a-button>
        </a-form-item>
      </a-form>

      <!-- —— 第二步（备选）：恢复码 —— -->
      <a-form
          v-else
          :model="formState"
          label-align="left"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 18 }"
          @finish="handleRecoveryLogin"
      >
        <a-alert type="warning" show-icon style="margin-bottom: 16px"
                 message="手机丢失/认证器不可用时，输入绑定时生成的一次性恢复码（每个只能用一次）"/>
        <a-form-item label="恢复码" name="recoveryCode"
                     :rules="[{ required: true, message: '请输入恢复码' }]">
          <a-input v-model:value="formState.recoveryCode" placeholder="恢复码"/>
        </a-form-item>
        <a-form-item :wrapper-col="{ offset: 6, span: 18 }">
          <a-button type="primary" html-type="submit" :loading="submitting">登录</a-button>
          <a-button style="margin-left: 8px" @click="step = 'totp'">返回动态码</a-button>
        </a-form-item>
      </a-form>

      <div style="text-align:center; margin-top: 12px">
        <a @click="router.push('/')">← 返回商城首页</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * [文件级说明] StaffLoginPage.vue —— 后台登录页（管理员/审计员）
 * ------------------------------------------------------------------
 * 两步登录流程：
 *   1. 第一步：用户名+密码 → 调 staffLogin()
 *       - 账号未绑定 TOTP：直接拿到 access_token（并标记 totp_setup_required）
 *         → 强制先跳 TOTP 绑定页；
 *       - 已绑定 TOTP：返回 step_token → 切到第二步界面；
 *   2. 第二步：输入认证器动态码（或切“恢复码”），调 staffLoginTotp /
 *      staffLoginRecovery → 拿到正式 access_token。
 * 登录成功后：token 存 localStorage（后续 axios 自动携带）、
 * 用户信息写入 Pinia store（角色 admin/auditor 供路由守卫与菜单判断），
 * 然后按角色跳转：管理员 → /admin/accounts，审计员 → /auditor/logs。
 */
import {reactive, ref} from 'vue';
import {message} from "ant-design-vue";
import {useRouter} from "vue-router";
import {staffLogin, staffLoginTotp, staffLoginRecovery} from '@/api/staff';
import {useLoginUserStore} from "@/store/useLoginUserStore";

const router = useRouter();
const loginUserStore = useLoginUserStore();

// 当前处于哪一步：password(第一步) / totp(动态码) / recovery(恢复码)
const step = ref<'password' | 'totp' | 'recovery'>('password');
const submitting = ref(false);
// 第一步成功后返回的预登录令牌（第二步请求时必须原样带回）
let stepToken = '';

// 登录表单数据（第一步与第二步共用）
const formState = reactive({
  username: '',
  password: '',
  totpCode: '',
  recoveryCode: '',
});

// 登录成功后统一处理：存 token + 写 store + 按角色跳转
const afterLogin = (data: any) => {
  localStorage.setItem('token', data.access_token);
  loginUserStore.setLoginUser({username: data.username, role: data.role});
  message.success('登录成功');
  if (data.totp_setup_required) {
    // 账号还没绑定 TOTP：先去绑定页完成绑定再进入后台
    router.push('/staff/totp/setup');
    return;
  }
  router.push(data.role === 'admin' ? '/admin/accounts' : '/auditor/logs');
};

// 请求异常统一提示：axios 抛错（后端未启动、请求被中断、500 且响应不是 JSON）时
// 也必须给用户可见反馈；否则页面只会 console.error，表现为“点了登录毫无反应”
const showRequestError = (e: any, fallback: string) => {
  const resp = e?.response;
  if (!resp) {
    message.error('无法连接后端服务，请确认后端已在 127.0.0.1:5000 启动');
    return;
  }
  const msg = resp.data?.message;
  message.error(msg ? `${fallback}：${msg}` : `${fallback}（HTTP ${resp.status}）`);
};

// 第一步：密码登录
const handlePasswordLogin = async (values: any) => {
  submitting.value = true;
  try {
    const res = await staffLogin({username: values.username, password: values.password});
    if (res.data.code === 0) {
      const d = res.data.data;
      if (d.need_totp) {
        stepToken = d.step_token;                 // 暂存，第二步使用
        step.value = 'totp';                       // “跳转”到第二步界面
      } else {
        afterLogin(d);                             // 未绑定：直接放行（随后强制绑定）
      }
    } else {
      message.error(res.data.message || '登录失败');
    }
  } catch (e) {
    console.error('后台登录失败:', e);
    showRequestError(e, '后台登录失败');
  } finally {
    submitting.value = false;
  }
};

// 第二步：TOTP 动态码登录
const handleTotpLogin = async (values: any) => {
  submitting.value = true;
  try {
    const res = await staffLoginTotp({step_token: stepToken, code: values.totpCode});
    if (res.data.code === 0) {
      afterLogin(res.data.data);
    } else {
      message.error(res.data.message || '动态码验证失败');
    }
  } catch (e) {
    console.error('TOTP登录失败:', e);
    showRequestError(e, '动态码验证失败');
  } finally {
    submitting.value = false;
  }
};

// 第二步（备选）：恢复码登录
const handleRecoveryLogin = async (values: any) => {
  submitting.value = true;
  try {
    const res = await staffLoginRecovery({step_token: stepToken, code: values.recoveryCode});
    if (res.data.code === 0) {
      message.warning('已用恢复码登录，请尽快重新绑定 TOTP');
      afterLogin(res.data.data);
    } else {
      message.error(res.data.message || '恢复码验证失败');
    }
  } catch (e) {
    console.error('恢复码登录失败:', e);
    showRequestError(e, '恢复码验证失败');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
/* 整页居中 + 浅色渐变背景（与用户登录页风格接近） */
#staffLoginPage {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ffffff 0%, #189fff 100%);
}
.staff-card {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}
.staff-title {
  text-align: center;
  margin-bottom: 24px;
}
</style>
