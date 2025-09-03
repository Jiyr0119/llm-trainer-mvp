<template>
  <!-- 错误处理组件不需要渲染任何内容 -->
</template>

<script setup>
import { onErrorCaptured, onMounted, inject } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();

// 全局错误处理
onErrorCaptured((error, instance, info) => {
  console.error('Vue错误被捕获:', error);
  console.error('错误来源组件:', instance);
  console.error('错误信息:', info);
  
  // 显示友好的错误提示
  ElMessage.error('应用发生错误，请刷新页面或联系管理员');
  
  // 对于严重错误，可以重定向到错误页面
  if (error.name === 'ChunkLoadError' || error.message.includes('Failed to fetch dynamically imported module')) {
    // 资源加载错误，可能是版本更新导致的
    router.push('/error/500');
  }
  
  // 返回false阻止错误继续传播
  return false;
});

// 监听全局未捕获的Promise错误
onMounted(() => {
  window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise错误:', event.reason);
    
    // 显示友好的错误提示
    ElMessage.error('操作失败，请稍后再试');
    
    // 阻止默认处理
    event.preventDefault();
  });
  
  // 监听全局JavaScript错误
  window.addEventListener('error', (event) => {
    console.error('全局JavaScript错误:', event.error);
    
    // 显示友好的错误提示
    ElMessage.error('应用发生错误，请刷新页面');
    
    // 阻止默认处理
    event.preventDefault();
  });
});
</script>