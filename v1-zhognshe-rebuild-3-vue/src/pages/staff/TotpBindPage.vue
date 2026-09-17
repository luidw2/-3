<template>
  <div id="totpBindPage">
    <a-card title="TOTP 双因素认证绑定" style="max-width: 720px; margin: 0 auto;">
      <!-- —— 绑定前：二维码 + 手动密钥 + 动态码确认 —— -->
      <template v-if="!bound">
        <a-steps :current="bindStep" size="small" style="margin-bottom: 20px">
          <a-step title="添加认证器"/>
          <a-step title="确认绑定"/>
        </a-steps>

        <a-alert type="info" show-icon style="margin-bottom: 16px"
                 message="用 Google Authenticator / Microsoft Authenticator 等应用扫描下方二维码（或手动输入密钥），然后输入应用上显示的 6 位动态码完成绑定"/>

        <div style="text-align: center; margin: 12px 0;">
          <canvas ref="qrCanvasRef" style="border:1px solid #eee; border-radius: 8px;"></canvas>
        </div>

        <a-descriptions :column="1" size="small" bordered style="margin-bottom: 16px">
          <a-descriptions-item label="手动密钥">
            <a-space>
              <span>{{ secret }}</span>
              <a-button size="small" @click="copySecret">复制</a-button>
            </a-space>
          </a-descriptions-item>
        </a-descriptions>

        <a-form layout="inline" style="justify-content: center; margin-bottom: 8px;">
          <a-form-item>
            <a-input v-model:value="confirmCode" maxlength="6"
                     placeholder="输入 6 位动态码" style="width: 220px"/>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" :loading="binding" @click="handleConfirm">确认绑定</a-button>
          </a-form-item>
        </a-form>
      </template>

      <!-- —— 绑定成功：一次性展示恢复码 —— -->
      <template v-else>
        <a-result status="success" title="TOTP 绑定成功">
          <template #subTitle>
            请务必保存以下 <b>一次性恢复码</b>（每个只能使用一次）。手机丢失或认证器不可用时，
            可凭恢复码登录后台；恢复码仅在此展示一次，请截图或抄写保存。
          </template>
          <template #extra>
            <a-card size="small" style="max-width: 460px; margin: 0 auto;">
              <a-space wrap style="justify-content:center">
                <a-tag v-for="(c, i) in recoveryCodes" :key="i" color="blue"
                       style="font-family: monospace; font-size: 14px; padding: 4px 8px;">
                  {{ c }}
                </a-tag>
              </a-space>
            </a-card>
            <div style="margin-top: 20px">
              <a-button type="primary" @click="finishAndRelogin">保存恢复码，去重新登录</a-button>
            </div>
          </template>
        </a-result>
      </template>
    </a-card>
  </div>
</template>

<script setup lang="ts">
/**
 * [文件级说明] TotpBindPage.vue —— TOTP 绑定页（管理员/审计员）
 * ------------------------------------------------------------------
 * 流程：
 *   1. 进入页面即调 totpSetup()：后端生成随机 Base32 secret 与 otpauth URI
 *      → 用 qrcode 库把 URI 画到 canvas 上（认证器扫码添加），同时展示
 *      手动密钥方便手动录入；
 *   2. 用户在认证器中看到动态码后回填 → 调 totpConfirm({secret, code})：
 *      后端校验动态码通过才把 secret 加密落库并启用 TOTP（totp_enabled=True）；
 *   3. 绑定成功响应里带有“一次性恢复码”明文（库中只存哈希）→ 本页展示一次；
 *      点击“保存恢复码，去重新登录”会**清除绑定前签发的旧令牌**、回到登录页，
 *      必须用“账号密码 + 动态码”重新登录后才进入后台 —— 保证两步认证真正生效
 *      （若沿用绑定前的旧 token，等同“绑了也能只输密码进后台”，失去意义）。
 */
import {nextTick, onMounted, ref} from 'vue';
import {message} from "ant-design-vue";
import {useRouter} from "vue-router";
import {totpSetup, totpConfirm} from '@/api/staff';
import {useLoginUserStore} from "@/store/useLoginUserStore";
import QRCode from 'qrcode';

const router = useRouter();
const loginUserStore = useLoginUserStore();

const qrCanvasRef = ref<HTMLCanvasElement | null>(null);
const secret = ref('');
const confirmCode = ref('');
const binding = ref(false);
const bound = ref(false);
const recoveryCodes = ref<string[]>([]);
const bindStep = ref(0);

// 进入页面即向后端申请绑定材料（本页受路由守卫保护：仅登录态 admin/auditor）
onMounted(async () => {
  try {
    const res = await totpSetup();
    if (res.data.code === 0) {
      secret.value = res.data.data.secret;
      bindStep.value = 0;
      // 把 otpauth URI 渲染成二维码（渲染到 canvas 上）
      await nextTick();
      await QRCode.toCanvas(qrCanvasRef.value, res.data.data.otpauth_uri,
          {width: 190, margin: 1});
    } else {
      // 已绑定过则提示，让用户直接进后台
      message.info(res.data.message || '该账号已绑定 TOTP');
      goRoleHome();
    }
  } catch (e) {
    console.error('获取TOTP绑定材料失败:', e);
  }
});

const copySecret = async () => {
  try {
    await navigator.clipboard.writeText(secret.value);
    message.success('密钥已复制');
  } catch (e) {
    message.info('复制失败，请手动抄写密钥');
  }
};

// 确认绑定：后端校验动态码通过后才会落库启用
const handleConfirm = async () => {
  if (!/^\d{6}$/.test(confirmCode.value)) {
    message.warning('请输入6位数字动态码');
    return;
  }
  binding.value = true;
  try {
    const res = await totpConfirm({secret: secret.value, code: confirmCode.value});
    if (res.data.code === 0) {
      bound.value = true;
      recoveryCodes.value = res.data.data.recovery_codes || [];
      message.success('TOTP 绑定成功');
    } else {
      message.error(res.data.message || '绑定失败');
    }
  } catch (e) {
    console.error('TOTP绑定失败:', e);
  } finally {
    binding.value = false;
  }
};

// 绑定完成后按角色进入对应后台首页（仅用于"账号已绑定、本身就走 TOTP 登录"的场景）
const goRoleHome = () => {
  const role = loginUserStore.loginUser?.role;
  router.push(role === 'auditor' ? '/auditor/logs' : '/admin/accounts');
};

// 绑定成功后的收尾：作废旧会话，强制"密码 + 动态码"重新登录
// 原因：绑定时携带的 token 是绑定前由"仅密码"签发，若不销毁，
//       用户会带着它直接进后台（两步认证形同虚设）；清掉后重登，
//       服务端因 totp_enabled=True 必然要求动态码，两步认证即刻生效。
const finishAndRelogin = () => {
  localStorage.removeItem('token');
  loginUserStore.setLoginUser({username: '未登录'});
  message.info('绑定成功！请用“账号密码 + 动态码”重新登录');
  router.push('/staff/login');
};
</script>

<style scoped>
#totpBindPage {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  padding: 20px;
}
</style>
