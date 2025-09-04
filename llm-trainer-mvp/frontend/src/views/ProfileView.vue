<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h2>个人资料</h2>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <el-form v-else :model="profileForm" :rules="rules" ref="profileFormRef" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="profileForm.username" disabled>
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email">
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="profileForm.full_name">
            <template #prefix>
              <el-icon><UserFilled /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="角色">
          <el-input v-model="profileForm.role" disabled>
            <template #prefix>
              <el-icon><Avatar /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-divider>修改密码</el-divider>
        
        <el-form-item label="新密码" prop="password">
          <el-input v-model="profileForm.password" :type="passwordVisible ? 'text' : 'password'" placeholder="留空表示不修改">
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
        
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="profileForm.confirmPassword" :type="confirmPasswordVisible ? 'text' : 'password'" placeholder="留空表示不修改">
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
          <el-button type="primary" :loading="saving" @click="handleUpdateProfile">保存修改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '../store/auth';
import { User, UserFilled, Message, Avatar, Lock, View, Hide } from '@element-plus/icons-vue';

const authStore = useAuthStore();
const profileFormRef = ref(null);
const loading = ref(true);
const saving = ref(false);
const passwordVisible = ref(false);
const confirmPasswordVisible = ref(false);

const profileForm = reactive({
  username: '',
  email: '',
  full_name: '',
  role: '',
  password: '',
  confirmPassword: ''
});

let originalProfile = null;

// 自定义验证器：确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (profileForm.password && value === '') {
    callback(new Error('请确认新密码'));
  } else if (profileForm.password && value !== profileForm.password) {
    callback(new Error('两次输入密码不一致'));
  } else {
    callback();
  }
};

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { min: 8, message: '密码长度不能小于8个字符', trigger: 'blur' },
    { pattern: /(?=.*[0-9])(?=.*[a-zA-Z])/, message: '密码必须包含数字和字母', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
};

const fetchUserProfile = async () => {
  loading.value = true;
  try {
    await authStore.fetchUserInfo();
    const userProfile = authStore.currentUser;
    
    if (userProfile) {
      profileForm.username = userProfile.username;
      profileForm.email = userProfile.email;
      profileForm.full_name = userProfile.full_name || '';
      profileForm.role = userProfile.role;
      profileForm.password = '';
      profileForm.confirmPassword = '';
      
      originalProfile = { ...profileForm };
    }
  } catch (error) {
    console.error('获取用户资料失败:', error);
    ElMessage.error('获取用户资料失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const handleUpdateProfile = () => {
  profileFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true;
      try {
        // 准备更新数据，只包含已修改的字段
        const updateData = {};
        
        if (profileForm.email !== originalProfile.email) {
          updateData.email = profileForm.email;
        }
        
        if (profileForm.full_name !== originalProfile.full_name) {
          updateData.full_name = profileForm.full_name;
        }
        
        if (profileForm.password) {
          updateData.password = profileForm.password;
        }
        
        // 只有当有数据需要更新时才调用API
        if (Object.keys(updateData).length > 0) {
          await authStore.updateUserInfo(updateData);
          ElMessage.success('个人资料更新成功');
          
          // 更新原始数据
          originalProfile = { ...profileForm };
          profileForm.password = '';
          profileForm.confirmPassword = '';
        } else {
          ElMessage.info('没有数据需要更新');
        }
      } catch (error) {
        console.error('更新个人资料失败:', error);
        ElMessage.error(error.message || '更新个人资料失败，请稍后重试');
      } finally {
        saving.value = false;
      }
    }
  });
};

const resetForm = () => {
  Object.assign(profileForm, { ...originalProfile, password: '', confirmPassword: '' });
  profileFormRef.value.clearValidate();
};

onMounted(() => {
  fetchUserProfile();
});
</script>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 30px auto;
  padding: 0 20px;
}

.profile-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.profile-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #303133;
}

.loading-container {
  padding: 20px 0;
}

.cursor-pointer {
  cursor: pointer;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset !important;
}

:deep(.el-divider__text) {
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}
</style>