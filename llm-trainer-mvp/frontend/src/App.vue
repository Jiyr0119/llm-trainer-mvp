<template>
  <!-- 应用根组件，包含导航栏和路由视图 -->
  <div id="app">
    <!-- 导航组件，提供应用的主要导航菜单 -->
    <Navigation />
    <!-- 路由视图，根据当前路由显示对应的页面组件 -->
    <router-view />
    <!-- 全局错误处理组件 -->
    <ErrorHandler />
  </div>
</template>

<script>
// 导入导航组件
import Navigation from './components/Navigation.vue'
// 导入错误处理组件
import ErrorHandler from './components/ErrorHandler.vue'

export default {
  name: 'App', // 组件名称
  components: {
    Navigation, // 注册导航组件，使其可在模板中使用
    ErrorHandler // 注册错误处理组件
  }
}
</script>

<style>
/* 应用全局样式 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif; /* 设置字体族 */
  -webkit-font-smoothing: antialiased; /* 字体平滑渲染（WebKit） */
  -moz-osx-font-smoothing: grayscale; /* 字体平滑渲染（Firefox） */
  color: #2c3e50; /* 文本颜色 */
  min-height: 100vh; /* 最小高度为视口高度，确保内容填满屏幕 */
}

/* Element Plus 头部组件样式覆盖 */
.el-header {
  background-color: #409EFF; /* 背景色 */
  color: #fff; /* 文字颜色 */
  text-align: center; /* 文本居中 */
  line-height: 60px; /* 行高 */
}

/* Element Plus 底部组件样式覆盖 */
.el-footer {
  background-color: #f5f5f5; /* 背景色 */
  color: #666; /* 文字颜色 */
  text-align: center; /* 文本居中 */
  line-height: 60px; /* 行高 */
}

/* Element Plus 主内容区样式覆盖 */
.el-main {
  background-color: #fff; /* 背景色 */
  color: #333; /* 文字颜色 */
  padding: 20px; /* 内边距 */
}
</style>