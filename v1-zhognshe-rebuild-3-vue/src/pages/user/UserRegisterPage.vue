<template>
  <div id="userRegisterPage">

    <div class="registerForm">

      <h2 class="title">用户注册</h2>
      <!-- 注册表单：用户名/密码/角色/证书密码/邮箱均必填，校验通过触发 @finish -->
      <a-form
          :model="formState"
          name="basic"

          label-align="left"

          :label-col="{ span: 4 }"
          :wrapper-col="{ span: 20 }"
          autocomplete="off"
          @finish="handleSubmit"
          @finishFailed="onFinishFailed"
      >
        <a-form-item
            label="用户名"
            name="username"
            :rules="usernameRules"
        >
          <a-input v-model:value="formState.username"
                   placeholder="请输入用户名"
                   @blur="formState.username = formState.username.trim()"
          />
        </a-form-item>

        <a-form-item
            label="密码"
            name="password"
            :rules="[{ required: true, message: '请输入密码' },{min :6,message:'密码长度最小为6'}]"
        >
          <a-input-password v-model:value="formState.password"
                            placeholder="请输入密码"
                            type="password"
          />
        </a-form-item>

        <!-- 新增角色选择 -->
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



        <!-- 证书密码：注册成功后后端会生成个人数字证书(PFX 文件)随响应返回下载，
             该密码用于打开/使用这张证书，后续“证书登录”需要再次输入同一密码 -->
        <a-form-item
            label="证书密码"
            name="certPassword"
            :rules="[{ required: true, message: '请输入证书密码' }]"
        >
          <a-input-password v-model:value="formState.certPassword"
                            placeholder="请输入证书密码"
                            type="password"
          />
        </a-form-item>




        <a-form-item
            label="邮箱"
            name="email"
            :rules="[{ required: true, message: '请输入邮箱' },{type: 'email', message: '请输入正确的邮箱格式'}]"
        >
          <a-input v-model:value="formState.email"
                   placeholder="请输入邮箱"
                   @blur="formState.email = formState.email.trim()"
          />
        </a-form-item>

        <a-form-item :wrapper-col="{ offset: 10, span: 10 }">
          <a-button type="primary" html-type="submit">注册</a-button>
        </a-form-item>
      </a-form>

      <a-form-item class="toLogin" style="text-align: center; margin-top: 16px;">
        <a @click="router.push('/user/login')" style="color: #1890ff; cursor: pointer;">
          已经注册了吗？点我登录
        </a>
      </a-form-item>

    </div>
  </div>
</template>


<script lang="ts" setup>
// ============================================================
// 页面：用户注册页（路由 /user/register）
// 用途：新用户注册。除常规的用户名/密码/邮箱外，还要求设置“证书密码”，
//       注册成功后后端会生成一张个人数字证书(PFX 文件)随响应一起返回。
// 流程：表单校验 -> 整理参数(用户名/邮箱去掉首尾空格) -> 调 userRegister()
//       -> 接口以二进制(blob)形式返回 .pfx 证书文件
//       -> 前端借助 Blob URL 触发浏览器下载（文件名形如“用户名_cert.pfx”）
//       -> 提示成功并跳转登录页，之后即可用该证书走“证书登录”。
// 说明：注册参数同样以 JSON 直接提交 POST /user/register，页面内未做前端加密。
//       由于该请求配置了 responseType:'blob'，后端返回的 JSON 错误信息也会以
//       Blob 形式到达前端，所以 getRegisterErrorMessage 里做了兼容解析。
// ============================================================
import {reactive} from 'vue';
import {userRegister} from '@/api/user'
import {message} from "ant-design-vue";
import {useRouter} from "vue-router";

// 注册表单数据类型：用户名、密码、证书密码、邮箱、角色
interface FormState {
  username: string;
  password: string;
  certPassword : string;
  email: string;
  role: string;
}


// 路由实例：注册成功后跳转登录页
const router = useRouter()


// 注册表单的响应式数据（与 a-form 双向绑定）
// 注：certPassword 的初始值 '123456' 为开发调试期默认值，正式使用时一般由用户自行设置
const formState = reactive<FormState>({
  username: '',
  password: '',
  email: '',
  certPassword:  '123456',
  role: 'user',
});

// 用户名的自定义校验规则：必填、长度 4-20、必须以英文字母开头且只含字母/数字/下划线
const usernameRules = [
  { required: true, message: '请输入用户名' },
  { min: 4, max: 20, message: '用户名长度必须为4-20个字符' },
  {
    pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/,
    message: '用户名必须以英文字母开头，只能包含字母、数字和下划线',
  },
];

// 组装提交参数：去掉用户名/邮箱首尾空格，其余字段原样保留
const buildRegisterPayload = (values: FormState): FormState => ({
  ...values,
  username: values.username.trim(),
  email: values.email.trim(),
});

// 从请求错误对象中解析出可展示的中文提示文案
// 兼容说明：注册接口设置了 responseType:'blob'，后端返回的 JSON 错误也会被包装成
//           Blob 到达这里，因此要先把它读成文本，再尝试解析成 JSON 提取 message
const getRegisterErrorMessage = async (error: any) => {
  const fallback = "注册请求失败，请稍后重试";
  const responseData = error?.response?.data;

  if (responseData instanceof Blob) {
    const text = await responseData.text();
    if (!text) {
      return fallback;
    }
    try {
      const json = JSON.parse(text);
      return json.message || json.error || fallback;
    } catch {
      return text;
    }
  }

  return responseData?.message || responseData?.error || fallback;
};


// 表单校验通过后的注册提交处理
const handleSubmit = async (values: any) => {
  try {
    // 先整理参数，再调用注册接口 POST /user/register
    const payload = buildRegisterPayload(values);
    console.log('Submit values:', payload);
    const res = await userRegister(payload);
    console.log('API response:', res);

    // 注册成功：后端以二进制流返回生成的数字证书(PFX 文件)。
    // 这里把 Blob 转成临时 URL，再模拟点击 <a download> 触发浏览器下载，
    // 下载文件名形如“<用户名>_cert.pfx”，下载完成后移除临时的 <a> 元素
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${payload.username}_cert.pfx`);
    document.body.appendChild(link);
    link.click();
    link.remove();

    // 提示注册成功（证书已下载，需妥善保管），随后跳转到登录页
    message.success("注册成功，证书已下载。请妥善保管PFX文件。")
    await router.push({
      path: "/user/login",
      replace: true,
    })
    console.log('Success:', payload);
  } catch (error: any) {
    console.error('注册失败:', error);
    message.error(await getRegisterErrorMessage(error));
  }
};


// 表单校验失败回调：某个必填项未填或格式错误时给出的提示
const onFinishFailed = (errorInfo: any) => {
  message.error("没看到提示吗？")
  console.log('Failed:', errorInfo);
};
</script>


<style scoped>
#userRegisterPage{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}
#userRegisterPage .registerForm{
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
  max-width: 480px;
  width: 100%;
}
#userRegisterPage .title {
  margin-bottom: 24px;
  text-align: center;
  color: #1a1a1a;
  font-size: 20px;
  font-weight: 600;
}
</style>
