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
      <!-- Logo和品牌名称 -->
      <div class="brand">
        <router-link :to="authStore.isLoggedIn ? '/home' : '/'" class="brand-link">
          <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="brand-logo" />
          <span class="brand-name">LLM训练平台</span>
        </router-link>
      </div>
      
      <!-- 各个导航菜单项，index属性对应路由路径 -->
      <el-menu-item v-if="!authStore.isLoggedIn" index="/">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/home">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/upload">
        <el-icon><Upload /></el-icon>
        <span>数据上传</span>
      </el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn && authStore.isAdmin" index="/admin">
        <el-icon><Setting /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn && authStore.isAdmin" index="/datasets">
        <el-icon><Files /></el-icon>
        <span>数据集管理</span>
      </el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/train">
        <el-icon><Setting /></el-icon>
        <span>模型训练</span>
      </el-menu-item>
      <el-menu-item v-if="authStore.isLoggedIn" index="/predict">
        <el-icon><DataAnalysis /></el-icon>
        <span>模型推理</span>
      </el-menu-item>
      
      <!-- 右侧环境信息 -->
      <div class="flex-spacer"></div>
      
      <!-- 用户未登录时显示登录和注册按钮 -->
      <template v-if="!authStore.isLoggedIn">
        <el-button 
          class="auth-btn login-btn" 
          @click="$router.push('/login')"
        >
          <el-icon><User /></el-icon>
          登录
        </el-button>
        <el-button 
          class="auth-btn register-btn" 
          @click="$router.push('/register')"
        >
          <el-icon><Plus /></el-icon>
          注册
        </el-button>
      </template>
      
      <!-- 用户已登录时显示用户菜单 -->
      <template v-else>
        <el-dropdown trigger="click" class="user-dropdown">
          <div class="user-info">
            <el-avatar :size="32" class="user-avatar">{{ authStore.currentUser?.username?.charAt(0).toUpperCase() || 'U' }}</el-avatar>
            <span class="username">{{ authStore.currentUser?.username || '用户' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">
                <el-icon><UserFilled /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
import { Setting, HomeFilled, Upload, Files, DataAnalysis, User, Plus, ArrowDown, UserFilled, SwitchButton } from '@element-plus/icons-vue'

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
  border-bottom: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  background: linear-gradient(to right, rgba(65, 88, 208, 0.95), rgba(200, 80, 192, 0.95));
  position: sticky;
  top: 0;
  z-index: 1000;
}

.el-menu {
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 20px;
  border-bottom: none !important;
  background-color: transparent !important;
}

.brand {
  margin-right: 30px;
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: white;
  font-weight: 700;
  font-size: 20px;
  transition: transform 0.3s ease;
}

.brand-link:hover {
  transform: translateY(-2px);
}

.brand-logo {
  width: 36px;
  height: 36px;
  margin-right: 10px;
}

.brand-name {
  font-size: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.el-menu-item {
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 16px;
  font-size: 15px;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.9) !important;
  border-bottom: 3px solid transparent !important;
}

.el-menu-item:hover, .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border-bottom: 3px solid white !important;
}

.el-menu-item .el-icon {
  margin-right: 8px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9) !important;
}

.el-menu-item.is-active .el-icon {
  color: white !important;
}

.flex-spacer {
  flex-grow: 1;
}

.auth-btn {
  margin: 0 8px;
  display: flex;
  align-items: center;
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
}

.auth-btn .el-icon {
  margin-right: 6px;
}

.login-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.login-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.register-btn {
  background-color: white;
  color: #4158D0;
}

.register-btn:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-dropdown {
  cursor: pointer;
  margin: 0 10px;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  background-color: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.user-avatar {
  background: linear-gradient(135deg, #C850C0, #FF6CAB);
  color: white;
  font-weight: bold;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: white;
  font-weight: 500;
}

.env-info-container {
  display: flex;
  align-items: center;
  padding: 0 15px;
  margin-left: 10px;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .brand-name,
  .username {
    display: none;
  }
  
  .el-menu {
    padding: 0 10px;
  }
  
  .el-menu-item {
    padding: 0 10px;
  }
}
</style>