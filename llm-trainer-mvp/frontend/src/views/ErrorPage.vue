<template>
  <div class="error-page">
    <div class="error-container">
      <el-result
        :icon="errorIcon"
        :title="errorTitle"
        :sub-title="errorSubTitle"
      >
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// 获取错误类型参数
const errorType = computed(() => route.params.type || '404');

// 根据错误类型设置不同的图标和文本
const errorIcon = computed(() => {
  switch (errorType.value) {
    case '403':
      return 'warning';
    case '500':
      return 'error';
    case '404':
    default:
      return 'info';
  }
});

const errorTitle = computed(() => {
  switch (errorType.value) {
    case '403':
      return '403 - 访问被禁止';
    case '500':
      return '500 - 服务器错误';
    case '404':
    default:
      return '404 - 页面不存在';
  }
});

const errorSubTitle = computed(() => {
  switch (errorType.value) {
    case '403':
      return '抱歉，您没有权限访问此页面';
    case '500':
      return '抱歉，服务器出现了问题，请稍后再试';
    case '404':
    default:
      return '抱歉，您访问的页面不存在';
  }
});

// 返回首页
const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.error-container {
  max-width: 500px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>