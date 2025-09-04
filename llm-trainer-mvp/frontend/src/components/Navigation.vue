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
      <el-menu-item v-if="authStore.isLoggedIn" index="/upload">数据上传</el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/datasets">数据集管理</el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/train">模型训练</el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/predict">模型推理</el-menu-item>
      
      <!-- 右侧环境信息 -->
      <div class="flex-spacer"></div>
      
      <!-- 用户未登录时显示登录和注册按钮 -->
      <template v-if="!authStore.isLoggedIn">
        <el-menu-item index="/login">登录</el-menu-item>
        <el-menu-item index="/register">注册</el-menu-item>
      </template>
      
      <!-- 用户已登录时显示用户菜单 -->
      <template v-else>
        <el-sub-menu index="user-menu">
          <template #title>{{ authStore.currentUser?.username || '用户' }}</template>
          <el-menu-item index="/profile">个人资料</el-menu-item>
          <el-menu-item @click="handleLogout">退出登录</el-menu-item>
        </el-sub-menu>
      </template>
      
      <div class="env-info-container">
        <EnvInfo />
      </div>
    </el-menu>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import EnvInfo from './EnvInfo.vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 检查登录状态
const checkLoginStatus = async () => {
  if (authStore.isLoggedIn) {
    try {
      // 获取当前用户信息
      await authStore.fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，可能是token过期，尝试刷新token
      try {
        await authStore.refreshToken()
        await authStore.fetchUserInfo()
      } catch (refreshError) {
        // 刷新token也失败，清除登录状态
        console.error('刷新token失败:', refreshError)
        authStore.logout()
      }
    }
  }
}

// 处理退出登录
const handleLogout = () => {
  authStore.logout()
  ElMessage.success('已成功退出登录')
  // 如果当前页面需要登录权限，则重定向到首页
  if (route.meta.requiresAuth) {
    router.push('/')
  }
}

onMounted(() => {
  // 组件创建时检查登录状态
  checkLoginStatus()
  // 监听登录状态变化事件
  window.addEventListener('auth-state-changed', checkLoginStatus)
})

onBeforeUnmount(() => {
  // 组件销毁前移除事件监听
  window.removeEventListener('auth-state-changed', checkLoginStatus)
})
</script>

<style scoped>
/* scoped属性确保样式仅应用于当前组件 */
.navigation {
  border-bottom: 1px solid #e6e6e6; /* 添加底部边框，提供视觉分隔 */
}

.el-menu {
  display: flex;
  align-items: center;
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