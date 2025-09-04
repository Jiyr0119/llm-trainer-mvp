<template>
  <div class="register-container">
    <div class="register-background"></div>
    <div class="register-content">
      <div class="brand-logo">
        <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="logo" />
        <h1 class="brand-name">LLM Trainer</h1>
      </div>
      <el-card class="register-card">
        <div class="card-header">
          <h2>创建账号</h2>
          <p class="subtitle">注册一个新账号以开始使用</p>
        </div>
      
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入邮箱"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input 
            v-model="registerForm.full_name" 
            placeholder="请输入姓名"
          >
            <template #prefix>
              <el-icon><UserFilled /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
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
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            :type="confirmPasswordVisible ? 'text' : 'password'" 
            placeholder="请再次输入密码"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
            <template #suffix>
              <el-icon @click="confirmPasswordVisible = !confirmPasswordVisible" class="cursor-pointer">
                <component :is="confirmPasswordVisible ? 'View' : 'Hide'" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            class="submit-btn" 
            :loading="authStore.isLoading" 
            @click="handleRegister"
          >
            <el-icon class="el-icon--left"><Plus /></el-icon> 注册
          </el-button>
        </el-form-item>
        
        <div class="form-footer">
          <span>已有账号? </span>
          <router-link to="/login" class="link">返回登录</router-link>
        </div>
      </el-form>
    </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '../store/auth';
import { User, UserFilled, Plus, Message, Lock, View, Hide } from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();
const registerFormRef = ref(null);

const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: ''
});

const passwordVisible = ref(false);
const confirmPasswordVisible = ref(false);

// 自定义验证器：确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'));
  } else {
    callback();
  }
};

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3到20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能小于8个字符', trigger: 'blur' },
    { pattern: /(?=.*[0-9])(?=.*[a-zA-Z])/, message: '密码必须包含数字和字母', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
};

const handleRegister = () => {
  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 准备注册数据，移除确认密码字段
        const { confirmPassword, ...registerData } = registerForm;
        
        // 使用Pinia存储的register action
        await authStore.register(registerData);
        
        // 显示成功消息
        ElMessage.success('注册成功，请登录');
        
        // 重定向到登录页面
        router.push('/login');
      } catch (error) {
        console.error('注册失败:', error);
        ElMessage.error(error.message || '注册失败，请稍后重试');
      }
    }
  });
};

</script>

<style scoped>
.register-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
  overflow: hidden;
}

.register-background {
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

.register-content {
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

.register-card {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.register-card:hover {
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
  .register-content {
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