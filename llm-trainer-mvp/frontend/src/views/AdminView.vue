<template>
  <div class="admin-view">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <h2>用户管理</h2>
          <el-button type="primary" @click="showAddUserDialog">添加用户</el-button>
        </div>
      </template>
      
      <!-- 用户列表 -->
      <el-table 
        v-loading="loading" 
        :data="users" 
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'ADMIN' ? 'danger' : 'primary'">
              {{ scope.row.role === 'ADMIN' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="180">
          <template #default="scope">
            {{ scope.row.last_login ? formatDate(scope.row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="scope">
            <el-button 
              size="small" 
              @click="showEditUserDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="confirmDeleteUser(scope.row)"
              :disabled="scope.row.id === currentUser.id"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username" v-if="!isEdit">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input 
            v-model="userForm.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password 
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="ADMIN" />
            <el-option label="普通用户" value="USER" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="userForm.is_active"
            active-text="激活"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm" :loading="submitting">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import userService from '../services/users';
import { useAuthStore } from '../store/auth';
import { storeToRefs } from 'pinia';

// 获取认证状态
const authStore = useAuthStore();
const { currentUser } = storeToRefs(authStore);

// 用户列表数据
const users = ref([]);
const loading = ref(false);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

// 表单相关
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const userFormRef = ref(null);
const userForm = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  role: 'USER',
  is_active: true
});

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const data = await userService.getAllUsers(skip, pageSize.value);
    users.value = data;
    total.value = data.length; // 实际应该从后端获取总数
  } catch (error) {
    ElMessage.error('获取用户列表失败');
    console.error('获取用户列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val;
  fetchUsers();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchUsers();
};

// 显示添加用户对话框
const showAddUserDialog = () => {
  isEdit.value = false;
  userForm.value = {
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'USER',
    is_active: true
  };
  dialogVisible.value = true;
};

// 显示编辑用户对话框
const showEditUserDialog = (user) => {
  isEdit.value = true;
  userForm.value = {
    id: user.id,
    email: user.email,
    full_name: user.full_name || '',
    role: user.role,
    is_active: user.is_active
  };
  dialogVisible.value = true;
};

// 提交用户表单
const submitUserForm = async () => {
  if (!userFormRef.value) return;
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        if (isEdit.value) {
          // 编辑用户
          await userService.updateUser(userForm.value.id, userForm.value);
          ElMessage.success('用户更新成功');
        } else {
          // 添加用户
          await userService.createUser(userForm.value);
          ElMessage.success('用户添加成功');
        }
        dialogVisible.value = false;
        fetchUsers(); // 刷新用户列表
      } catch (error) {
        ElMessage.error(error.message || (isEdit.value ? '更新用户失败' : '添加用户失败'));
        console.error(isEdit.value ? '更新用户失败:' : '添加用户失败:', error);
      } finally {
        submitting.value = false;
      }
    }
  });
};

// 确认删除用户
const confirmDeleteUser = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      loading.value = true;
      try {
        await userService.deleteUser(user.id);
        ElMessage.success('用户删除成功');
        fetchUsers(); // 刷新用户列表
      } catch (error) {
        ElMessage.error('删除用户失败');
        console.error('删除用户失败:', error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除');
    });
};

// 页面加载时获取用户列表
onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.admin-view {
  padding: 20px;
}

.admin-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
</style>