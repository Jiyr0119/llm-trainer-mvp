import axiosInstance from './axios';
import { ElMessage } from 'element-plus';

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

// 用户认证服务
const authService = {
  // 用户注册
  register(userData) {
    return handleResponse(axiosInstance.post('/api/auth/register', userData));
  },

  // 用户登录
  login(username, password) {
    return handleResponse(axiosInstance.post('/api/auth/login', { username, password }));
  },

  // 刷新令牌
  refreshToken(refreshToken) {
    return handleResponse(axiosInstance.post('/api/auth/refresh', { refresh_token: refreshToken }));
  },

  // 获取当前用户信息
  getCurrentUser() {
    return handleResponse(axiosInstance.get('/api/auth/me'));
  },

  // 更新用户信息
  updateUserInfo(userData) {
    return handleResponse(axiosInstance.put('/api/auth/me', userData));
  },

  // 保存令牌到本地存储
  saveTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  },

  // 从本地存储获取访问令牌
  getAccessToken() {
    return localStorage.getItem('access_token');
  },

  // 从本地存储获取刷新令牌
  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  },

  // 清除本地存储的令牌
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // 检查用户是否已登录
  isLoggedIn() {
    return !!this.getAccessToken();
  },

  // 用户登出
  logout() {
    this.clearTokens();
    // 可以在这里添加其他登出逻辑，如重定向到登录页面
  }
};

export default authService;