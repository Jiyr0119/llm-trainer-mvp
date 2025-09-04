import axiosInstance from './axios';

// 统一处理API响应
const handleResponse = (promise) => {
  return promise.then(response => {
    // 统一处理标准格式: { success: true, data: [...] }
    if (response && response.success === true) {
      return response.data || response;
    } else {
      return Promise.reject(response);
    }
  });
};

// 用户管理服务
const userService = {
  // 获取所有用户（仅管理员）
  getAllUsers(skip = 0, limit = 100) {
    return handleResponse(axiosInstance.get(`/api/users?skip=${skip}&limit=${limit}`));
  },

  // 根据ID获取用户（仅管理员）
  getUserById(userId) {
    return handleResponse(axiosInstance.get(`/api/users/${userId}`));
  },

  // 创建用户（仅管理员）
  createUser(userData) {
    return handleResponse(axiosInstance.post('/api/users', userData));
  },

  // 更新用户（仅管理员）
  updateUser(userId, userData) {
    return handleResponse(axiosInstance.put(`/api/users/${userId}`, userData));
  },

  // 删除用户（仅管理员）
  deleteUser(userId) {
    return handleResponse(axiosInstance.delete(`/api/users/${userId}`));
  }
};

export default userService;