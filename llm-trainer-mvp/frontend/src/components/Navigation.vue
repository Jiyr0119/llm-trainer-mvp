<template>
  <!-- 导航组件容器 -->
  <div class="navigation">
    <!-- Element Plus菜单组件 -->
    <el-menu
      :default-active="$route.path" 
      class="el-menu-demo"
      mode="horizontal" 
      router
    >
      <!-- 各个导航菜单项，index属性对应路由路径 -->
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/upload">数据上传</el-menu-item>
      <el-menu-item index="/datasets">数据集管理</el-menu-item>
      <el-menu-item index="/train">模型训练</el-menu-item>
      <el-menu-item index="/predict">模型推理</el-menu-item>
      
      <!-- 右侧环境信息 -->
      <div class="flex-spacer"></div>
      <div class="env-info-container">
        <EnvInfo />
      </div>
    </el-menu>
  </div>
</template>

<script>
import EnvInfo from './EnvInfo.vue'

export default {
  name: 'Navigation', // 组件名称，用于调试和开发工具中的标识
  components: {
    EnvInfo // 注册环境信息组件
  }
}
</script>

<style scoped>
/* scoped属性确保样式仅应用于当前组件 */
.navigation {
  border-bottom: 1px solid #e6e6e6; /* 添加底部边框，提供视觉分隔 */
}

.flex-spacer {
  flex-grow: 1; /* 占用所有可用空间，将后续元素推到右侧 */
}

.env-info-container {
  display: flex;
  align-items: center;
  padding: 0 15px;
}
</style>