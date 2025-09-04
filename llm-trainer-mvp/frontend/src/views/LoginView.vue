<template>
  <div class="login-container">
    <div class="login-background" style="opacity: 0.8;"></div>
    <div class="login-content">
      <div class="brand-logo">
        <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="logo" />
        <h1 class="brand-name">LLM Trainer</h1>
      </div>
      <el-card class="login-card">
        <div class="card-header">
          <h2>欢迎回来</h2>
          <p class="subtitle">登录您的账号以继续使用</p>
        </div>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top">
        <el-form-item label="用户名或邮箱" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名或邮箱"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            :type="passwordVisible ? 'text' : 'password'" 
            placeholder="请输入密码"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
            <template #suffix>
              <el-icon @click="passwordVisible = !passwordVisible" class="cursor-pointer">
                <component :is="passwordVisible ? 'View' : 'Hide'" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <div class="forgot-password">
          <router-link to="/forgot-password" class="link">忘记密码?</router-link>
        </div>
        
        <el-form-item>
          <el-button 
            type="primary" 
            class="submit-btn" 
            :loading="authStore.isLoading" 
            @click="handleLogin"
          >
            <el-icon class="el-icon--left"><Key /></el-icon> 登录
          </el-button>
        </el-form-item>
        
        <div class="form-footer">
          <span>还没有账号? </span>
          <router-link to="/register" class="link">立即注册</router-link>
        </div>
      </el-form>
    </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '../store/auth';
import { User, Lock, Key, View, Hide } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const loginFormRef = ref(null);
const loginForm = reactive({
  username: '',
  password: ''
});

const passwordVisible = ref(false);

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能小于8个字符', trigger: 'blur' }
  ]
};

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 使用Pinia存储的login action
        await authStore.login({
          username: loginForm.username,
          password: loginForm.password
        });
        
        // 显示成功消息
        ElMessage.success('登录成功');
        
        // 重定向到首页或之前的页面
        const redirectPath = route.query.redirect || '/';
        router.push(redirectPath);
      } catch (error) {
        console.error('登录失败:', error);
        ElMessage.error(error.message || '登录失败，请检查用户名和密码');
      }
    }
  });
};

</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('../assets/login-bg.svg');
  background-size: cover;
  background-position: center;
  z-index: -1;
}

.login-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 500px;
  z-index: 1;
}

.brand-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  width: 80px;
  height: 80px;
  margin-bottom: 10px;
}

.brand-name {
  font-size: 28px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  margin: 0;
}

.login-card {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  font-size: 28px;
  background: linear-gradient(45deg, #4158D0, #C850C0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 10px;
  font-weight: 600;
}

.subtitle {
  color: #606266;
  font-size: 14px;
  margin-top: 8px;
}

.forgot-password {
  text-align: right;
  margin-bottom: 20px;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(45deg, #4158D0, #C850C0);
  border: none;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  background: linear-gradient(45deg, #3a4ec0, #b745af);
}

.cursor-pointer {
  cursor: pointer;
}

.form-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.link {
  color: #4158D0;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.link:hover {
  color: #C850C0;
  text-decoration: none;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .login-content {
    max-width: 90%;
  }
  
  .brand-logo {
    margin-bottom: 20px;
  }
  
  .logo {
    width: 60px;
    height: 60px;
  }
  
  .brand-name {
    font-size: 24px;
  }
}
</style>