<script setup lang="ts">
// ============================================================
// 页面：个人中心 / 个人信息页（路由 /user/profile）
// 用途：展示当前登录用户的基本信息（id、用户名、角色、创建时间）；
//       右上角提供“修改个人信息”“删除账号”入口，底部提供“登出”按钮。
// 数据来源：本页不主动发请求，直接读取全局登录用户 store（loginUserStore.loginUser），
//       该数据由登录成功后 fetchLoginUser()（内部调 GET /user/profile）写入。
// 登出流程：userLogOut()（POST /user/logout）-> 后端 code===0 时
//       清除 localStorage 中的 token、把 store 用户重置为“未登录”，再跳回登录页。
// ============================================================

import {useLoginUserStore} from "@/store/useLoginUserStore"
import {useRouter} from "vue-router"



import {reactive} from 'vue';
import {userLogOut} from '@/api/user'
import {message} from "ant-design-vue";

// 表单数据结构声明：保留用户名/密码字段
// （当前模板未绑定具体输入项，提交给登出接口的即为此表单模型值）
interface FormState {
  username: string;
  password: string;
}


// 路由实例与全局登录用户 store（登出时用于重置用户状态 / 跳转登录页）
const router = useRouter()
const loginUserStore = useLoginUserStore();


// 登出表单的响应式数据：模板中实际只放了一个“登出”提交按钮，字段结构保留备扩展
const formState = reactive<FormState>({
  username: '',
  password: '',
});

// “登出”提交处理：请求后端登出接口并清理前端的本地登录态
const handleSubmit = async (values: any) => {
  try {
    console.log('Submit values:', values);
    // 调用登出接口 POST /user/logout，请后端注销当前会话
    const res = await userLogOut(values);
    console.log('API response:', res);

    // code === 0：后端确认登出成功，开始清理前端本地登录状态
    if (res.data.code === 0) {
      // 清除localStorage中的token
      localStorage.removeItem('token');
      // 重置用户信息
      loginUserStore.setLoginUser({ username: '未登录' });
      // 提示登出成功并跳回登录页（replace 防止浏览器回退再次进入本页）
      message.success("登出成功")
      await router.push({
        path: "/user/login",
        replace: true,
      })

      console.log('Success:', values);
    } else {
      message.error(res.data.message || "登出失败")
    }
  } catch (error) {
    console.error('登出失败:', error);
    // 尝试从错误对象中获取错误信息
    let errorMessage = "登出请求失败，请稍后重试";
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    message.error(errorMessage);
  }

};

// a-form 的校验失败回调（本页表单未配置校验规则，一般不会触发，保留以备扩展）
const onFinishFailed = (errorInfo: any) => {
  message.error("表单校验未通过，请检查填写内容")
  console.log('Failed:', errorInfo);
};







</script>

<template>
  <div id="userProfile">

    <div class="container">

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


        <!-- 个人信息卡片：展示内容全部取自全局 store 中的当前登录用户数据 -->
        <a-card title="个人信息" style="width: 300px">
          <!-- 卡片右上角操作区：跳转“修改个人信息”页 / “删除账号”页 -->
          <template #extra>
            <a @click="router.push('/user/update')" style="color: #1890ff; cursor: pointer; margin-right: 16px;">
              修改个人信息
            </a>
            <a @click="router.push('/user/delete')" style="color: #ff4d4f; cursor: pointer;">
              删除账号
            </a>
          </template>

          <p>id： {{ loginUserStore.loginUser.user_id }}</p>
          <p>用户名：{{ loginUserStore.loginUser.username }}</p>
          <p>角色： {{ loginUserStore.loginUser.role === 'user' ? '客户' : loginUserStore.loginUser.role === 'seller' ? '商家' : loginUserStore.loginUser.role }}</p>
          <p>创建时间： {{ loginUserStore.loginUser.created_at }}</p>
        </a-card>


        <!-- 登出按钮：html-type="submit" 会提交 a-form，从而触发 @finish=handleSubmit 执行登出 -->
        <a-form-item :wrapper-col="{ offset: 10, span: 10 }">
          <a-button type="primary" html-type="submit">登出</a-button>
        </a-form-item>


      </a-form>

    </div>
  </div>
</template>

<style scoped>
#userProfile {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  width: 100%;
  padding: 20px;
}

#userProfile .container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
  max-width: 480px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 8px solid white;
  outline: 1px solid #e8e8e8;
}

#userProfile .container a-card {
  width: 100%;
  max-width: 300px;
}
</style>