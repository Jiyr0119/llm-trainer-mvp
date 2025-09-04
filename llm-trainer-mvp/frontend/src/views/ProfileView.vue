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
          <el-input v-model="profileForm.username" disabled></el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email"></el-input>
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="profileForm.full_name"></el-input>
        </el-form-item>
        
        <el-form-item label="角色">
          <el-input v-model="profileForm.role" disabled></el-input>
        </el-form-item>
        
        <el-divider>修改密码</el-divider>
        
        <el-form-item label="新密码" prop="password">
          <el-input v-model="profileForm.password" type="password" placeholder="留空表示不修改"></el-input>
        </el-form-item>
        
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="profileForm.confirmPassword" type="password" placeholder="留空表示不修改"></el-input>
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

const authStore = useAuthStore();
const profileFormRef = ref(null);
const loading = ref(true);
const saving = ref(false);

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
  display: flex;
  justify-content: center;
  padding: 20px;
}

.profile-card {
  width: 100%;
  max-width: 600px;
}

.card-header {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}
</style>