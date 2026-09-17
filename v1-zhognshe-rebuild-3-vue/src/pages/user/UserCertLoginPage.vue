<template>
  <div id="certLoginPage">
    <div class="certLoginform">
      <h2 class="title">证书登录</h2>

      <!-- 数字证书登录表单：选择 .pfx/.crt 证书文件 + 证书密码 + 角色后提交 -->
      <a-form
        :model="formState"
        name="basic"
        label-align="left"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 20 }"
        @finish="handleSubmit"
      >
        <a-form-item label="证书文件" required>
          <!-- 替换为原生 input -->
          <input
            type="file"
            ref="fileInput"
            accept=".pfx,.crt"
            @change="handleFileChange"
          />
          <div v-if="certFile" class="file-info">
            已选择: {{ certFile.name }}
          </div>
        </a-form-item>

        <a-form-item label="证书密码" required>
          <a-input-password v-model:value="formState.password" placeholder="请输入证书密码" />
        </a-form-item>

        <a-form-item
          label="角色"
          name="role"
          :rules="[{ required: true, message: '请选择角色' }]"
        >
          <a-radio-group v-model:value="formState.role">
            <a-radio value="user">用户</a-radio>
            <a-radio value="seller">商家</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item :wrapper-col="{ offset: 10, span: 10 }">
          <a-button type="primary" html-type="submit">登录</a-button>
        </a-form-item>
      </a-form>

      <a-form-item class="toLogin" style="text-align: center; margin-top: 16px;">
        <a @click="router.push('/user/login')" style="color: #1890ff; cursor: pointer;">
          不想用证书登录？点我密码登录
        </a>
      </a-form-item>
    </div>
  </div>
</template>

<script lang="ts" setup>
// ============================================================
// 页面：数字证书登录页（路由 /user/certLogin）
// 用途：区别于“账号密码登录”，用个人数字证书(PFX/CRT 文件) + 证书密码完成认证，
//       体现“证书即身份凭证”的 PKI/数字证书认证思路（教学演示用）。
// 流程：本地选择 .pfx/.crt 文件 -> 校验扩展名 -> 把“证书文件 + 密码 + 角色”
//       封装成 FormData(multipart) 提交 POST /user/certLogin
//       -> 成功后手动保存 access_token / refresh_token / cert_thumbprint
//       -> 调 fetchLoginUser() 拉取用户信息 -> 跳转首页。
// 说明：证书登录接口不在 request.js“自动保存 token”的名单中（那仅针对 /user/login），
//       因此本页需要显式把返回的令牌写入 localStorage。
// ============================================================
import { ref, reactive } from 'vue';
import { userCertLogin } from '@/api/user';
import { useLoginUserStore } from '@/store/useLoginUserStore';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';

// 路由实例与全局登录用户 store（跳转、拉取用户信息用）
const router = useRouter();
const loginUserStore = useLoginUserStore();
// 用户选择的数字证书文件（.pfx / .crt），未选择时为 null
const certFile = ref<File | null>(null);
// 登录表单数据：证书密码 + 登录角色（默认 user）
const formState = reactive({
  password: '',
  role: 'user',
});

// 文件选择事件回调：读取用户选择的证书文件
// 原生 input 的 change 处理
const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const file = input.files[0];
    // 检查文件扩展名
    const fileName = file.name;
    const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
    if (ext !== '.pfx' && ext !== '.crt') {
      message.error('请上传 .pfx 或 .crt 格式的证书文件');
      input.value = ''; // 清空 input，允许重新选择同一文件
      certFile.value = null;
      return;
    }
    certFile.value = file;
  } else {
    certFile.value = null;
  }
};

// 提交数字证书登录：把证书、密码、角色打包后发送给后端
const handleSubmit = async () => {
  // 前端兜底校验：未选择证书文件时直接拦截并提示，不发请求
  if (!certFile.value) {
    message.error('请选择证书文件');
    return;
  }

  // 使用 FormData 承载“证书文件 + 密码 + 角色”，提交时自动按 multipart/form-data 编码
  const formData = new FormData();
  formData.append('cert', certFile.value);         // 数字证书文件本体
  formData.append('password', formState.password); // 证书密码
  formData.append('role', formState.role);         // 登录角色

  try {
    // 调用证书登录接口 POST /user/certLogin（涉及文件上传、耗时较长，
    // request.js 中已把 axios 超时时间放宽到 100 秒）
    const response = await userCertLogin(formData);
    console.log('API response:', response);

    // code === 0 表示后端验证证书通过、登录成功
    if (response.data.code === 0) {
      // 证书登录不在 request.js“自动保存 token”的名单里（自动保存仅针对 /user/login），
      // 因此这里手动把访问令牌与刷新令牌写入 localStorage；
      // 之后普通请求会由请求拦截器读取并附带 Authorization 请求头
      localStorage.setItem('token', response.data.data.access_token);
      localStorage.setItem('refresh_token', response.data.data.refresh_token);


      // 后端若返回证书指纹 cert_thumbprint 则一并保存，
      // 可据此识别当前登录使用的是哪一张数字证书
      if (response.data.data.cert_thumbprint) {
        localStorage.setItem('cert_thumbprint', response.data.data.cert_thumbprint);
        console.log('证书指纹:', response.data.data.cert_thumbprint);
      } else {
        console.warn('响应中没有 cert_thumbprint 字段');
      }


      // 拉取当前用户信息到全局 store（内部调 GET /user/profile），随后提示成功
      await loginUserStore.fetchLoginUser();
      message.success('登录成功');
      await router.push({
        path: "/",
        replace: true,
      });
    } else {
      message.error(response.data.message || '登录失败');
    }
  } catch (error: any) {
    console.error('登录失败:', error);
    let errorMessage = "登录请求失败，请稍后重试";
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    message.error(errorMessage);
  }
};
</script>

<style scoped>
#certLoginPage {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}
#certLoginPage .certLoginform {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
  max-width: 480px;
  width: 100%;
}
#certLoginPage .title {
  margin-bottom: 24px;
  text-align: center;
  color: #1a1a1a;
  font-size: 20px;
  font-weight: 600;
}
.file-info {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}
</style>