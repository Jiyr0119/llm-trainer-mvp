import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getErrorMessage, getErrorType, ERROR_TYPES } from '../utils/errorCodes'

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_API_URL || 'http://localhost:8001',
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
axiosInstance.interceptors.request.use(
  config => {
    // 从本地存储获取访问令牌
    const token = localStorage.getItem('access_token')
    // 如果令牌存在，添加到请求头
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 是否正在刷新令牌的标志
let isRefreshing = false;
// 等待令牌刷新的请求队列
let refreshSubscribers = [];

// 将请求添加到队列
const subscribeTokenRefresh = (cb) => refreshSubscribers.push(cb);

// 执行队列中的请求
const onRefreshed = (token) => {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
};

// 刷新令牌
const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('刷新令牌不可用');
    }
    
    // 直接使用axios而不是axiosInstance，避免循环调用拦截器
    const response = await axios.post(
      `${import.meta.env.VITE_APP_API_URL || 'http://localhost:8001'}/auth/refresh`,
      { refresh_token: refreshToken },
      { headers: { 'Content-Type': 'application/json' } }
    );
    
    // 检查响应格式
    if (!response.data || !response.data.access_token || !response.data.refresh_token) {
      throw new Error('刷新令牌响应格式无效');
    }
    
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return access_token;
  } catch (error) {
    // 记录详细错误信息
    console.error('刷新令牌失败:', error);
    
    // 检查是否有响应数据
    if (error.response && error.response.data) {
      console.error('刷新令牌错误详情:', error.response.data);
    }
    
    // 刷新令牌失败，清除所有令牌
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // 触发自定义事件，通知应用程序令牌刷新失败
    window.dispatchEvent(new CustomEvent('auth-token-refresh-failed', {
      detail: { error: error.message || '刷新令牌失败' }
    }));
    
    throw error;
  }
};

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    // 如果响应成功，直接返回数据
    return response.data;
  },
  async (error) => {
    // 获取原始请求配置
    const originalRequest = error.config;
    
    // 处理HTTP错误
    let errorMessage = '未知错误';
    let errorCode = 'UNKNOWN_ERROR';
    let errorData = null;
    
    if (error.response) {
      // 服务器返回了错误状态码和数据
      const { status, data } = error.response;
      
      // 处理401错误（未授权）- 可能是令牌过期或令牌类型错误
      if (status === 401 && !originalRequest._retry) {
        // 检查错误消息是否与令牌类型相关
        const isTokenTypeError = data && 
          (data.message?.includes('token type') || 
           data.message?.includes('令牌类型') || 
           data.code === 'INVALID_TOKEN_TYPE');
        
        // 如果是令牌类型错误，直接清除令牌并重定向到登录页面
        if (isTokenTypeError) {
          console.error('令牌类型错误:', data.message);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        // 标记该请求已尝试过重试，避免无限循环
        originalRequest._retry = true;
        
        // 如果当前没有其他请求正在刷新令牌
        if (!isRefreshing) {
          isRefreshing = true;
          
          try {
            // 尝试刷新令牌
            const newToken = await refreshToken();
            
            // 更新原始请求的Authorization头
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            
            // 通知所有等待的请求
            onRefreshed(newToken);
            
            // 重试原始请求
            return axiosInstance(originalRequest);
          } catch (refreshError) {
            // 刷新令牌失败，重定向到登录页面
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            isRefreshing = false;
          }
        } else {
          // 如果已经有请求正在刷新令牌，将当前请求加入队列
          return new Promise(resolve => {
            subscribeTokenRefresh(token => {
              originalRequest.headers['Authorization'] = `Bearer ${token}`;
              resolve(axiosInstance(originalRequest));
            });
          });
        }
      }
      
      // 优先使用后端返回的错误信息和错误码
      if (data && data.code) {
        errorCode = data.code;
        // 使用错误码映射获取用户友好的错误信息
        errorMessage = getErrorMessage(data.code, data.message || '操作失败');
      } else if (data && data.message) {
        errorMessage = data.message;
      } else {
        // 如果后端没有提供详细信息，根据HTTP状态码生成默认消息
        switch (status) {
          case 400:
            errorMessage = '请求参数错误';
            break;
          case 401:
            errorMessage = '未授权，请登录';
            break;
          case 403:
            errorMessage = '拒绝访问';
            break;
          case 404:
            errorMessage = '请求的资源不存在';
            break;
          case 500:
            errorMessage = '服务器内部错误';
            break;
          default:
            errorMessage = `服务器错误 (${status})`;
        }
      }
      
      // 获取错误数据
      if (data && data.data) {
        errorData = data.data;
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMessage = '网络错误，服务器未响应';
      errorCode = 'NETWORK_ERROR';
    } else {
      // 请求配置出错
      errorMessage = `请求错误: ${error.message}`;
      errorCode = 'REQUEST_ERROR';
    }
    
    // 根据错误类型显示不同的提示样式
    const errorType = getErrorType(errorCode);
    
    if (errorType === ERROR_TYPES.SYSTEM_ERROR) {
      // 系统错误，显示警告样式
      ElMessage({
        message: errorMessage,
        type: 'error',
        duration: 5000,
        showClose: true
      });
    } else if (errorType === ERROR_TYPES.USER_ERROR) {
      // 用户错误，显示警告样式
      ElMessage({
        message: errorMessage,
        type: 'warning',
        duration: 4000
      });
    } else {
      // 可恢复错误，显示信息样式
      ElMessage({
        message: errorMessage,
        type: 'info',
        duration: 3000
      });
    }
    
    // 返回标准化的错误对象
    return Promise.reject({
      success: false,
      message: errorMessage,
      code: errorCode,
      data: errorData,
      type: errorType
    });
  }
)

export default axiosInstance