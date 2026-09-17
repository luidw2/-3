<template>
  <div id="userDelete">
    <!-- 注销(删除)账号表单：危险操作，需要“二次确认文本 + 原密码”双重确认 -->
    <div class="deleteForm">
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

        <a-form-item label="是否确认删除" name="delete_or">
          <a-radio-group v-model:value="formState.delete_or">
            <a-radio :value="true">是</a-radio>
            <a-radio :value="false">否</a-radio>
          </a-radio-group>
        </a-form-item>

        <!-- 防误删确认机制：勾选“确认删除”后，必须手动输入指定内容(DELETE) 才能提交 -->
        <a-form-item v-if="formState.delete_or" label="输入指定内容" name="content_fix">
            <a-input v-model:value="formState.content_fix" placeholder="DELETE"/>
        </a-form-item>

        <!-- 原密码二次校验：证明是账号本人在执行删除操作 -->
        <a-form-item label="请输入原先密码进行确认" name="password">
          <a-input v-model:value="formState.password" type="password"/>
        </a-form-item>


        <a-form-item :wrapper-col="{ span: 14, offset: 4 }">
          <a-button type="primary" @click="onSubmit">确认</a-button>
          <a-button style="margin-left: 10px" @click="resetForm">Reset</a-button>
        </a-form-item>

      </a-form>
    </div>

  </div>
</template>


<script lang="ts" setup>
// ============================================================
// 页面：注销(删除)账号页（路由 /user/delete）
// 用途：永久删除当前账号。属于高风险操作，页面设置了“双重确认”：
//       1) 必须勾选“确认删除”并手动输入指定内容(DELETE)（content_fix）；
//       2) 必须输入“原密码”（password）做二次身份验证。
// 流程：点“确认” -> formRef.validate() 整体校验（含 content_fix 的自定义校验）
//       -> 组装 {name, confirmation, password} -> userDelete()
//       （DELETE /user/delete）-> code===0 成功后提示并跳回登录页
//       （账号已注销，之后可用同一用户名重新注册）。
// ============================================================
import {reactive, ref} from 'vue';
import type {UnwrapRef} from 'vue';
import type {Rule} from 'ant-design-vue/es/form';
import {message} from "ant-design-vue";
import {useRouter} from "vue-router";
import {useLoginUserStore} from '@/store/useLoginUserStore'
import {userDelete} from '@/api/user'

// 删除确认表单的数据结构：用户名、是否确认删除、确认文本(DELETE)、原密码
interface FormState {
  name: string;
  delete_or: boolean;
  content_fix: string;
  password: string;
}

const loginUserStore = useLoginUserStore(); // 读取当前登录用户名作为表单默认值
const router = useRouter()                  // 删除成功后跳回登录页
const formRef = ref();                      // 表单组件引用：用于整体校验与重置
const labelCol = {span: 11};                // 表单“标签”列栅格宽度
const wrapperCol = {span: 10};              // 表单“输入控件”列栅格宽度
// 删除确认表单的响应式数据：用户名默认带出当前登录用户；
// delete_or 默认 false（未勾选确认时不显示确认文本输入框，从交互上防止误删）
const formState: UnwrapRef<FormState> = reactive({
  name: loginUserStore.loginUser.username || '',
  delete_or: false,
  content_fix: '',
  password: ''
});
// 表单校验规则：name / delete_or / password 必填，content_fix 走下面的自定义校验
const rules: Record<string, Rule[]> = {
  name: [
    {required: true, message: '请输入用户名', trigger: 'change'},
    {min: 6, message: '长度最小为6', trigger: 'blur'},
  ],
  delete_or: [{required: true, message: '选择是否删除', trigger: 'change'}],
  content_fix: [
    {
      // 自定义校验逻辑：当用户选择“确认删除”时，必须填写确认文本(DELETE)，否则校验不通过
      validator: (rule, value, callback) => {
        if (formState.delete_or && !value) {
          callback('请输入确认文本');
        } else {
          callback();
        }
      },
      trigger: 'change'
    }
  ],
  password: [{required: true, message: '请输入密码', trigger: 'change'}],
};
// 点击“确认”按钮：整体校验通过后组装参数，调用删除接口
const onSubmit = async () => {
  try {
    // 触发表单整体校验（含 content_fix 的自定义校验），不通过会进入 catch
    await formRef.value.validate();
    console.log('Submit values:', formState);

    // 构建与后端期望一致的数据结构
    // confirmation=二次确认文本(DELETE)，password=原密码，两者共同证明是本人操作
    const deleteData: any = {
      name: formState.name,
      confirmation: formState.content_fix,
      password: formState.password,//用户之前的密码，用做二次验证
    };

    // 调用删除接口 DELETE /user/delete（账号将被永久注销）
    const res = await userDelete(deleteData);

    // code === 0 表示删除成功：跳回登录页，此后可用同一用户名重新注册
    if (res.data.code === 0) {
      message.success("删除成功")
      await router.push({
        path: "/user/login",
        replace: true,
      })

      console.log('Success:', deleteData);
    } else {
      message.error(res.data.message || "删除失败")
    }
  } catch (error) {
    console.error('删除失败:', error);
    // 尝试从错误对象中获取错误信息
    let errorMessage = "删除请求失败，请稍后重试";
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    message.error(errorMessage);
  }
};
// “Reset”按钮：把表单重置为初始状态
const resetForm = () => {
  formRef.value.resetFields();
};
</script>


<style scoped>

#userDelete {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  width: 100%;
  padding: 20px;
}

.deleteForm {
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