<template>
  <div id="userUpdate">
    <!-- 修改个人信息表单：支持修改用户名/角色，并可选是否同时修改密码 -->
    <div class="updateForm">
      <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          :label-col="labelCol"
          :wrapper-col="wrapperCol"
      >
        <a-form-item ref="name" label="用户名" name="name">
          <a-input v-model:value="formState.name"/>
        </a-form-item>

        <a-form-item label="角色" name="role">
          <a-radio-group v-model:value="formState.role">
            <a-radio value="user">用户</a-radio>
            <a-radio value="seller">商家</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="是否修改密码" name="password_fix_or">
          <a-radio-group v-model:value="formState.fixOr">
            <a-radio :value="true">是</a-radio>
            <a-radio :value="false">否</a-radio>
          </a-radio-group>
        </a-form-item>

        <!-- 仅在“是否修改密码”选“是”时渲染“新密码”输入框（由 v-if 控制显隐） -->
        <a-form-item v-if="formState.fixOr" label="修改密码" name="password_fix">
            <a-input v-model:value="formState.password_fix"/>
        </a-form-item>

        <!-- 二次身份确认：修改资料必须提供“原先密码”，防止账号被他人随意篡改 -->
        <a-form-item label="请输入原先密码进行确认" name="password">
          <a-input v-model:value="formState.password" type="password"/>
        </a-form-item>


        <a-form-item :wrapper-col="{ span: 14, offset: 4 }">
          <a-button type="primary" @click="onSubmit">提交</a-button>
          <a-button style="margin-left: 10px" @click="resetForm">Reset</a-button>
        </a-form-item>

      </a-form>
    </div>
  </div>
</template>


<script lang="ts" setup>
// ============================================================
// 页面：修改个人信息页（路由 /user/update）
// 用途：修改当前用户的用户名/角色；可选择是否顺带修改登录密码。
// 安全设计：无论是否改密码，都必须填写“原密码”作为二次身份校验（current_password）；
//          只有勾选“修改密码”时才在请求里附带新密码 password 字段。
// 流程：点“提交” -> formRef.validate() 做整体校验 -> 组装请求体
//       {username, current_password[, password]} -> userUpdate()
//       （PUT /user/update）-> code===0 成功后 fetchLoginUser() 刷新全局 store
//       -> 提示成功并跳回个人资料页。
// ============================================================
import {reactive, ref} from 'vue';
import type {UnwrapRef} from 'vue';
import type {Rule} from 'ant-design-vue/es/form';
import {message} from "ant-design-vue";
import {useRouter} from "vue-router";
import {useLoginUserStore} from '@/store/useLoginUserStore'
import {userUpdate} from '@/api/user'

// 修改表单的数据类型：
// name=新用户名，role=角色，fixOr=是否同时修改密码，
// password_fix=新密码（仅 fixOr 为 true 时有效），password=原密码（二次校验用）
interface FormState {
  name: string;
  role: string | undefined;
  fixOr: boolean;
  password_fix: string;
  password: string;
}

const loginUserStore = useLoginUserStore(); // 修改成功后用来刷新 store 中的用户资料
const router = useRouter()                  // 修改成功后跳回个人资料页
const formRef = ref();                      // 表单组件引用：用于整体校验与重置
const labelCol = {span: 11};                // 表单“标签”列栅格宽度
const wrapperCol = {span: 10};              // 表单“输入控件”列栅格宽度
// 修改表单的响应式数据（模板通过 v-model 与之双向绑定）
// name 初始值取自当前登录用户的用户名（loginUserStore.loginUser.username），
// 进入页面即显示本人账号；若 store 尚未加载成功则回退为空字符串等待手动输入
const formState: UnwrapRef<FormState> = reactive({
  name: loginUserStore.loginUser?.username || '',
  role: 'user',
  fixOr: false,
  password_fix: '',
  password: ''
});
// 表单校验规则：key 与各 a-form-item 的 name 一一对应，触发时机为 change / blur
const rules: Record<string, Rule[]> = {
  name: [
    {required: true, message: '请输入用户名', trigger: 'change'},
    {min: 6, message: '长度最小为6', trigger: 'blur'},
  ],
  role: [{required: true, message: '请选择你的角色', trigger: 'change'}],
  fixOr: [{required: true, message: '是否需要重置密码', trigger: 'change'}],
  password_fix: [{required: true, message: '请输入新密码', trigger: 'change'}],
  password: [{required: true, message: '请输入密码', trigger: 'change'}],
};
// 点击“提交”按钮：先做整体校验，通过后组装数据调用修改接口
const onSubmit = async () => {
  try {
    // 触发表单整体校验：任一字段不满足 rules 都会抛错并进入 catch
    await formRef.value.validate();
    console.log('Submit values:', formState);
    
    // 构建与后端期望一致的数据结构
    // 注意：表单中的“角色”radio 并未包含在提交数据里（能否修改角色以后端接口约定为准）
    const updateData: any = {
      username: formState.name,              // 修改后的用户名
      current_password: formState.password,//用户之前的密码，用做二次验证
    };
    
    // 如果选择修改密码，添加密码字段
    if (formState.fixOr) {
      updateData.password = formState.password_fix;
    }
    
    console.log('Update data:', updateData);
    // 调用修改接口 PUT /user/update
    const res = await userUpdate(updateData);
    console.log('API response:', res);

    // code === 0 表示后端修改成功
    if (res.data.code === 0) {
      console.log('Update successful, data:', res.data.data);
      // 更新用户信息
      console.log('Before updateLoginUser');
      await loginUserStore.fetchLoginUser()
      console.log('After updateLoginUser, loginUser:', loginUserStore.loginUser);
      // 提示修改成功并跳回个人资料页（replace 避免浏览器回退重新提交本表单）
      message.success("修改成功")
      await router.push({
        path: "/user/profile",
        replace: true,
      })

      console.log('Success:', updateData);
    } else {
      message.error(res.data.message || "修改失败")
    }
  } catch (error) {
    console.error('修改失败:', error);
    // 尝试从错误对象中获取错误信息
    let errorMessage = "修改请求失败，请稍后重试";
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    message.error(errorMessage);
  }
};
// “Reset”按钮：把表单所有字段重置为初始值
const resetForm = () => {
  formRef.value.resetFields();
};
</script>


<style scoped>
#userUpdate {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  width: 100%;
  padding: 20px;
}

.updateForm {
  text-align: center;
  margin: 0;
  box-sizing: border-box;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
  max-width: 480px;
  width: 100%;
}

</style>