<template> 
   <!-- 页面根节点：整页 flex 居中，白色卡片中展示“创建商品”表单 -->
   <div id="createProductPage"> 
     <div class="productForm"> 
       <h2 class="title">创建商品</h2> 
       <a-form 
           ref="formRef" 
           :model="formState" 
           name="product_create" 
           label-align="left" 
           :label-col="{ span: 4 }" 
           :wrapper-col="{ span: 20 }" 
           autocomplete="off" 
           @finish="handleSubmit" 
           @finishFailed="onFinishFailed" 
       > 
         <!-- 商品名称 --> 
         <a-form-item 
             label="商品名称" 
             name="name" 
             :rules="[{ required: true, message: '请输入商品名称' }]" 
         > 
           <a-input 
               v-model:value="formState.name" 
               placeholder="请输入商品名称" 
               :maxlength="100" 
           /> 
         </a-form-item> 
 
         <!-- 价格（单位：元） -->
         <a-form-item
           label="价格 (元)"
           name="priceYuan"
           :rules="[
             { required: true, message: '请输入价格' },
             { validator: validatePriceYuan }
           ]"
         >
           <a-input-number
               v-model:value="formState.priceYuan"
               :min="0"
               :step="0.01"
               :precision="2"
               placeholder="请输入价格（单位：元）"
               style="width: 100%"
           />
           <div class="field-tip">支持两位小数，例如 9.99 表示九元九角九分</div>
         </a-form-item>

         <!-- 商品描述 -->
         <a-form-item
             label="商品描述"
             name="description"
         >
           <a-textarea
               v-model:value="formState.description"
               placeholder="请输入商品描述（选填）"
               :auto-size="{ minRows: 3, maxRows: 6 }"
               :maxlength="500"
               show-count
           />
         </a-form-item>

         <!-- 商品照片 -->
         <!-- 上传组件说明：before-upload 先校验 JPG/PNG 格式与 2MB 大小；custom-request 只是前端模拟上传，
              选中的文件暂存在 uploadedFile，真正的图片上传在提交表单时随 FormData 一起发送给后端 -->
         <a-form-item
             label="商品照片"
             name="image"
         >
           <a-upload
             v-model:file-list="fileList"
             :max-count="1"
             :show-upload-list="true"
             :before-upload="beforeUpload"
             :on-remove="onRemove"
             :custom-request="customRequest"
             accept="image/*"
           >
             <a-button>
               <upload-outlined></upload-outlined>
               上传照片
             </a-button>
           </a-upload>
           <div class="field-tip">支持 JPG、PNG 格式，每个商品最多上传 1 张照片</div>
         </a-form-item>

         <!-- 商品状态 -->
         <a-form-item
             label="商品状态"
             name="status"
             :rules="[{ required: true, message: '请选择商品状态' }]"
         >
           <a-radio-group v-model:value="formState.status">
             <a-radio value="active">上架 (active)</a-radio>
             <a-radio value="inactive">下架 (inactive)</a-radio>
           </a-radio-group>
         </a-form-item>

         <!-- 操作按钮 -->
         <!-- “创建商品”是 submit 类型按钮：表单校验通过触发 handleSubmit，校验失败触发 onFinishFailed；
              “重置”按钮调用 handleReset 清空输入并恢复默认状态 -->
         <a-form-item :wrapper-col="{ offset: 4, span: 20 }">
           <a-button
               type="primary"
               html-type="submit"
               :loading="loading"
               style="margin-right: 12px"
           >
             创建商品
           </a-button>
           <a-button @click="handleReset">重置</a-button>
         </a-form-item>
       </a-form>
     </div>
   </div>
 </template>

 <script lang="ts" setup>
 // ============================================================
 // 页面级注释：ProductCreatePage.vue —— 商家“发布商品”页面
 // 功能：商家填写商品名称、价格（元）、描述，上传 1 张商品照片，选择上架/下架状态
 //       后点击“创建商品”，把数据提交给后端 createProduct 接口完成发布。
 // 关键设计：
 //  1) 价格输入以“元”为单位并支持两位小数；提交时用 Math.round(price*100) 换算成
 //     “分”（整数）传给后端，避免浮点数精度问题；
 //  2) 图片上传是前端模拟：before-upload 校验格式(JPG/PNG)与大小(<2MB)，custom-request
 //     延时 1 秒回调成功，选中的文件仅暂存在 uploadedFile，并未真正上传；真正上传发生在
 //     提交时——把文件与商品字段一起放进 FormData 发给后端；
 //  3) 表单校验由 a-form 声明式规则完成；后端统一响应 code===0 视为创建成功，
 //     随后跳转到商家商品管理页（replace 替换历史，返回键不会回到已清空的发布页）。
 // ============================================================
 import { reactive, ref } from 'vue';
 import { message } from 'ant-design-vue';
 import { UploadOutlined } from '@ant-design/icons-vue';
 // 引入后端商品接口 createProduct（创建商品，请求体为 FormData）
 import { createProduct } from '@/api/product';
 import {useRouter} from "vue-router";
 // 路由实例：商品创建成功后可跳转到“商家商品管理页”
 const router = useRouter()

 // 表单引用，用于重置
 const formRef = ref();

 // 加载状态
 const loading = ref(false);

 // 文件列表
 const fileList = ref([]);
 // 上传的文件对象
 const uploadedFile = ref(null);

 // 表单数据类型（priceYuan 用于前端展示，单位为元）
 interface ProductFormState {
   name: string;
   priceYuan: number | null;
   description: string;
   status: 'active' | 'inactive';
 }

 // 表单初始值
 const formState = reactive<ProductFormState>({
   name: '',
   priceYuan: null,
   description: '',
   status: 'active',
 });

 // 文件上传前验证
 const beforeUpload = (file) => {
   const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
   if (!isJpgOrPng) {
     message.error('只能上传 JPG/PNG 格式的图片！');
     return false;
   }
   const isLt2M = file.size / 1024 / 1024 < 2;
   if (!isLt2M) {
     message.error('图片大小不能超过 2MB！');
     return false;
   }
   return true;
 };

 // 文件移除时的处理
 const onRemove = (file) => {
   uploadedFile.value = null;
   fileList.value = [];
 };

 // 自定义上传逻辑
 const customRequest = (options) => {
   const { file, onSuccess, onError } = options;
   uploadedFile.value = file;
   // 模拟上传成功
   setTimeout(() => {
     onSuccess?.(file);
   }, 1000);
 };

 // 自定义价格校验（元，非负，最多两位小数）
 const validatePriceYuan = async (_rule: any, value: number | null) => {
   if (value === null || value === undefined) {
     return Promise.reject('请输入价格');
   }
   if (value < 0) {
     return Promise.reject('价格不能为负数');
   }
   // 由于 precision=2 已经限制了输入，这里仅做二次校验
   const decimalPart = value.toString().split('.')[1];
   if (decimalPart && decimalPart.length > 2) {
     return Promise.reject('价格最多保留两位小数');
   }
   return Promise.resolve();
 };

 // 表单提交处理
 const handleSubmit = async (values: ProductFormState) => {
   loading.value = true;
   try {
     // 将元转换为分（整数），Math.round 处理浮点数精度问题
     const priceInCents = Math.round(values.priceYuan! * 100);

     // 创建 FormData 对象
     const formData = new FormData();
     formData.append('name', values.name);
     formData.append('price', priceInCents.toString());
     formData.append('description', values.description || '');
     formData.append('status', values.status);

     // 如果有上传的文件，添加到 FormData
     if (uploadedFile.value) {
       formData.append('image', uploadedFile.value);
     }

     // 调用后端 createProduct 接口提交商品数据（FormData 含图片文件及各字段）
     const res = await createProduct(formData);

     // 根据后端统一响应结构判断 (code: 0 表示成功)
     if (res.data.code === 0) {
       message.success('商品创建成功！');
       // 重置表单，保留 status 默认值 'active'
       formRef.value?.resetFields();
       // 重置文件列表
       fileList.value = [];
       uploadedFile.value = null;
       // 创建成功：跳转到商家商品管理页查看新商品（replace 替换历史记录，返回键不会回到已提交页面）
       await router.push({
        path: "/seller/products/profile",
        replace: true,
       })


     } else {
       // 处理后端返回的业务错误
       message.error(res.data.message || '创建失败，请稍后重试');
     }
   } catch (error: any) {
     console.error('创建商品失败:', error);
     // 尝试从错误响应中提取后端返回的 message
     let errorMsg = '创建商品请求失败，请稍后重试';
     if (error.response?.data?.message) {
       errorMsg = error.response.data.message;
     } else if (error.response?.data?.error) {
       errorMsg = error.response.data.error;
     }
     message.error(errorMsg);
   } finally {
     loading.value = false;
   }
 };

 // 表单校验失败回调
 const onFinishFailed = (errorInfo: any) => {
   console.log('表单校验失败:', errorInfo);
   message.warning('请按照提示正确填写商品信息');
 };

 // 重置表单
 const handleReset = () => {
   formRef.value?.resetFields();
   // 确保状态重置为 'active'（resetFields 会恢复到初始值）
 };
 </script>

 <style scoped>
 #createProductPage {
   min-height: 100vh;
   display: flex;
   align-items: center;
   justify-content: center;
   background-color: #21c6fd;
   padding: 20px;
 }

 #createProductPage .productForm {
   background-color: white;
   border-radius: 8px;
   box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
   padding: 32px;
   max-width: 600px;
   width: 100%;
 }

 #createProductPage .title {
   margin-bottom: 28px;
   text-align: center;
   color: #1a1a1a;
   font-size: 22px;
   font-weight: 600;
 }

 .field-tip {
   font-size: 12px;
   color: #8c8c8c;
   margin-top: 4px;
   line-height: 1.5;
 }

 /* 让 a-input-number 宽度自适应 */
 :deep(.ant-input-number) {
   width: 100%;
 }
 </style>