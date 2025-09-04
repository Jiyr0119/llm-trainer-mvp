<template>
  <div class="forgot-password-container">
    <div class="forgot-password-background"></div>
    <div class="forgot-password-content">
      <div class="brand-logo">
        <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="logo" />
        <h1 class="brand-name">LLM Trainer</h1>
      </div>
      <el-card class="forgot-password-card">
        <div class="card-header">
          <h2>忘记密码</h2>
          <p class="subtitle">请输入您的用户名或邮箱，我们将发送重置密码的链接</p>
        </div>
      
        <el-form :model="forgotForm" :rules="rules" ref="forgotFormRef" label-position="top">
          <el-form-item label="用户名或邮箱" prop="username">
            <el-input 
              v-model="forgotForm.username" 
              placeholder="请输入您的用户名或邮箱"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="submit-btn" 
              :loading="loading" 
              @click="handleSubmit"
            >
              <el-icon class="el-icon--left"><Message /></el-icon> 发送重置链接
            </el-button>
          </el-form-item>
          
          <div class="form-footer">
            <router-link to="/login" class="link">返回登录</router-link>
          </div>
        </el-form>
        
        <el-result 
          v-if="submitted" 
          icon="success" 
          title="重置链接已发送" 
          sub-title="请检查您的邮箱，按照邮件中的指示重置密码"
        >
          <template #extra>
            <router-link to="/login">
              <el-button type="primary">返回登录</el-button>
            </router-link>
          </template>
        </el-result>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { User, Message } from '@element-plus/icons-vue';

const forgotFormRef = ref(null);
const loading = ref(false);
const submitted = ref(false);

const forgotForm = reactive({
  username: ''
});

const rules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ]
};

const handleSubmit = () => {
  forgotFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 这里应该调用后端API发送重置密码邮件
        // 由于后端暂未实现该功能，这里模拟成功响应
        setTimeout(() => {
          submitted.value = true;
          loading.value = false;
        }, 1500);
      } catch (error) {
        ElMessage.error(error.message || '发送重置链接失败，请稍后重试');
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.forgot-password-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
  overflow: hidden;
}

.forgot-password-background {
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

.forgot-password-content {
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

.forgot-password-card {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.forgot-password-card:hover {
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

.form-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
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
  .forgot-password-content {
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