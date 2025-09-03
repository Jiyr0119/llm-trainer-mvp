import axios from 'axios'
import { ElMessage } from 'element-plus'

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
    // 可以在这里添加认证token等
    // if (store.getters.token) {
    //   config.headers['Authorization'] = `Bearer ${store.getters.token}`
    // }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    // 如果响应成功，直接返回数据
    return response.data;
  },
  (error) => {
    // 处理HTTP错误
    let errorMessage = '未知错误';
    let errorCode = 'UNKNOWN_ERROR';
    let errorData = null;
    
    if (error.response) {
      // 服务器返回了错误状态码和数据
      const { status, data } = error.response;
      
      // 使用后端返回的错误信息（如果有）
      if (data && data.message) {
        errorMessage = data.message;
      }
      
      // 使用后端返回的错误码（如果有）
      if (data && data.code) {
        errorCode = data.code;
      }
      
      // 使用后端返回的错误数据（如果有）
      if (data && data.data) {
        errorData = data.data;
      }
      
      // 如果后端没有提供详细信息，根据HTTP状态码生成默认消息
      if (!data || !data.message) {
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
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMessage = '网络错误，服务器未响应';
      errorCode = 'NETWORK_ERROR';
    } else {
      // 请求配置出错
      errorMessage = `请求错误: ${error.message}`;
      errorCode = 'REQUEST_ERROR';
    }
    
    // 显示错误消息
    ElMessage.error(errorMessage);
    
    // 返回标准化的错误对象
    return Promise.reject({
      success: false,
      message: errorMessage,
      code: errorCode,
      data: errorData
    });
  }
)

export default axiosInstance