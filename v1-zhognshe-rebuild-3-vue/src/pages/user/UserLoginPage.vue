<template>
  <div id="userLoginPage">

    <div class="loginform">

      <h2 class="title">用户登录</h2>

      <!-- 用户登录表单（ant-design-vue）：与 formState 双向绑定；
           点击“登录”触发 @finish=handleSubmit，校验失败则触发 @finishFailed -->
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
            :rules="[{ required: true, message: '请输入用户名' },{min :6,message:'用户名长度最小为6'}]"
        >
          <a-input v-model:value="formState.username"
                   placeholder="请输入用户名"
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

        <!-- 页脚快捷入口：未注册 → 注册页；已持数字证书 → 证书登录页 -->
        <a-form-item class="toRegister" style="text-align: center; margin-top: 16px;">
        <a @click="router.push('/user/register')" style="color: #1890ff; cursor: pointer;">
          还没注册吗？点我注册
        </a>

          <a-form-item class="toRegister" style="text-align: center; margin-top: 16px;">
        <a @click="router.push('/user/certLogin')" style="color: #18ffe4; cursor: pointer;">
          快来证书登录吧
        </a>
      </a-form-item>
      </a-form-item>

    </div>
  </div>
</template>


<script lang="ts" setup>
// ============================================================
// 页面：用户登录页（路由 /user/login）
// 用途：账号 + 密码 + 角色 的普通登录入口（区别于“数字证书登录”）。
// 流程：表单校验通过 -> handleSubmit 调 userLogin() 提交
//       -> 后端返回业务码 code === 0 表示成功
//       -> request.js 的响应拦截器会自动把 access_token 存入 localStorage
//       -> 再调用 loginUserStore.fetchLoginUser() 拉取当前用户信息到全局 store
//       -> 提示“登录成功”并跳转首页。
// 注意：本页代码中未出现 RSA/SM2 等前端加解密与验证码逻辑，用户名/密码/角色
//       以 JSON 直接提交给后端接口 POST /user/login（加密等安全机制以后端实现为准）。
// ============================================================
import {reactive} from 'vue';
import {userLogin} from '@/api/user'
import {useLoginUserStore} from '@/store/useLoginUserStore'
import {message} from "ant-design-vue";
import {useRouter} from "vue-router";

// 登录表单的数据结构：用户名 / 密码 / 所选角色
interface FormState {
  username: string;
  password: string;
  role: string;
}


// 路由实例（跳转首页用）；loginUserStore：全局登录用户状态（pinia store）
const router = useRouter()
const loginUserStore = useLoginUserStore();


// 登录表单的响应式数据，与 a-form 双向绑定；角色默认选中“用户(user)”
const formState = reactive<FormState>({
  username: '',
  password: '',
  role: 'user',
});
// 表单校验通过后的提交处理：请求后端登录接口并分发处理结果
const handleSubmit = async (values: any) => {
  try {
    // 不输出包含密码的信息
    console.log('Submit values:');
    console.log('Username:', values.username);
    console.log('Role:', values.role);
    // 调用登录接口 POST /user/login（请求封装见 src/request.js）
    // 说明：登录成功时 request.js 的响应拦截器会自动把 access_token 写入 localStorage
    const res = await userLogin(values);
    console.log('API response:', res);

    // 后端业务码 code === 0 代表登录成功
    if (res.data.code === 0) {
      console.log('Login successful, token:', res.data.data?.token);
      // 登录成功后：通过 store 拉取当前用户资料（内部调用 GET /user/profile），供全站展示使用
      // 先获取用户信息
      console.log('Before fetchLoginUser');
      await loginUserStore.fetchLoginUser()
      console.log('After fetchLoginUser, loginUser:', loginUserStore.loginUser);
      // 提示成功并跳转首页（replace 使登录页不残留在浏览器历史里）
      message.success("登录成功")
      await router.push({
        path: "/",
        replace: true,
      })

      // 登录成功，不输出包含密码的信息
      console.log('Login successful');
      console.log('Username:', values.username);
      console.log('Role:', values.role);
    } else {
      message.error(res.data.message || "登录失败")
    }
  } catch (error) {
    console.error('登录失败:', error);
    // 尝试从错误对象中获取错误信息
    let errorMessage = "登录请求失败，请稍后重试";
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    message.error(errorMessage);
  }

};

// 表单校验失败回调：用户名/密码等未填写或长度不足时给出的提示
const onFinishFailed = (errorInfo: any) => {
  message.error("表单校验未通过：请按要求填写用户名/密码后再登录")
  console.log('Failed:', errorInfo);
};
</script>


<style scoped>
#userLoginPage{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}
#userLoginPage .loginform{
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
  max-width: 480px;
  width: 100%;
}
#userLoginPage .title {
  margin-bottom: 24px;
  text-align: center;
  color: #1a1a1a;
  font-size: 20px;
  font-weight: 600;
}
</style>