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

<script setup>
// 导入导航组件
import Navigation from './components/Navigation.vue'
// 导入错误处理组件
import ErrorHandler from './components/ErrorHandler.vue'

// 使用setup语法，不再需要显式注册组件和返回选项对象
</script>

<style>
/* 应用全局样式 */
:root {
  --primary-color: #6366f1;
  --primary-light: #818cf8;
  --primary-dark: #4f46e5;
  --secondary-color: #10b981;
  --secondary-light: #34d399;
  --secondary-dark: #059669;
  --accent-color: #f59e0b;
  --accent-light: #fbbf24;
  --accent-dark: #d97706;
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
  --text-tertiary: #9ca3af;
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --info-color: #3b82f6;
}

#app {
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif; /* 更现代的字体族 */
  -webkit-font-smoothing: antialiased; /* 字体平滑渲染（WebKit） */
  -moz-osx-font-smoothing: grayscale; /* 字体平滑渲染（Firefox） */
  color: var(--text-primary); /* 使用变量控制文本颜色 */
  min-height: 100vh; /* 最小高度为视口高度，确保内容填满屏幕 */
  background-color: var(--bg-secondary); /* 使用变量控制背景色 */
}

/* 全局按钮样式增强 */
.el-button {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.el-button--primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--primary-color));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

/* 全局卡片样式增强 */
.el-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Element Plus 头部组件样式覆盖 */
.el-header {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)); /* 渐变背景 */
  color: #fff; /* 文字颜色 */
  text-align: center; /* 文本居中 */
  line-height: 60px; /* 行高 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); /* 添加阴影 */
}

/* Element Plus 底部组件样式覆盖 */
.el-footer {
  background-color: var(--bg-tertiary); /* 使用变量控制背景色 */
  color: var(--text-secondary); /* 使用变量控制文字颜色 */
  text-align: center; /* 文本居中 */
  line-height: 60px; /* 行高 */
  border-top: 1px solid rgba(0, 0, 0, 0.05); /* 添加顶部边框 */
}

/* Element Plus 主内容区样式覆盖 */
.el-main {
  background-color: var(--bg-primary); /* 使用变量控制背景色 */
  color: var(--text-primary); /* 使用变量控制文字颜色 */
  padding: 24px; /* 增加内边距 */
}

/* 全局输入框样式增强 */
.el-input__inner {
  border-radius: 6px;
  transition: all 0.3s ease;
}

.el-input__inner:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

/* 全局过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>