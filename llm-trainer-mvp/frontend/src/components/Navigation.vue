<template>
  <!-- 导航组件容器 -->
  <div class="navigation">
    <!-- Element Plus菜单组件 -->
    <el-menu
      :default-active="$route.path" <!-- 根据当前路由路径设置活动菜单项 -->
      class="el-menu-demo"
      mode="horizontal" <!-- 水平模式菜单 -->
      router <!-- 启用路由模式，自动处理导航 -->
    >
      <!-- 各个导航菜单项，index属性对应路由路径 -->
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/upload">数据上传</el-menu-item>
      <el-menu-item index="/datasets">数据集管理</el-menu-item>
      <el-menu-item index="/train">模型训练</el-menu-item>
      <el-menu-item index="/predict">模型推理</el-menu-item>
    </el-menu>
  </div>
</template>

<script>
export default {
  name: 'Navigation' // 组件名称，用于调试和开发工具中的标识
}
</script>

<style scoped>
/* scoped属性确保样式仅应用于当前组件 */
.navigation {
  border-bottom: 1px solid #e6e6e6; /* 添加底部边框，提供视觉分隔 */
}
</style>