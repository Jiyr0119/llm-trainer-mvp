import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8001',
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
  response => {
    // 处理统一的响应格式
    const res = response.data
    
    // 如果响应包含code字段，说明是新的统一格式
    if (res.code !== undefined) {
      if (res.code === 200) {
        // 成功响应，直接返回数据部分
        return {
          ...response,
          data: res.data || res // 兼容旧格式，如果没有data字段，返回整个响应
        }
      } else {
        // 业务逻辑错误
        ElMessage.error(res.message || '请求失败')
        return Promise.reject(new Error(res.message || '未知错误'))
      }
    }
    
    // 旧格式直接返回
    return response
  },
  error => {
    console.error('Response error:', error)
    
    // 错误处理
    const { response } = error
    if (response) {
      // 服务器返回了错误响应
      const { status, data } = response
      let message = '请求失败'
      
      // 检查是否是新的统一格式
      if (data && data.code && data.message) {
        message = data.message
      } else if (data && data.detail) {
        message = data.detail
      } else {
        // 根据状态码定制错误信息
        switch (status) {
          case 400:
            message = '请求参数错误'
            break
          case 401:
            message = '未授权，请登录'
            break
          case 403:
            message = '拒绝访问'
            break
          case 404:
            message = '请求的资源不存在'
            break
          case 500:
            message = '服务器内部错误'
            break
          default:
            message = `请求失败(${status})`
        }
      }
      
      ElMessage.error(message)
    } else {
      // 请求没有到达服务器
      ElMessage.error('网络错误，请检查您的网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default axiosInstance