// 全局应用状态管理 - Pinia版本
import { defineStore } from 'pinia'

// 定义全局应用状态存储
export const useAppStore = defineStore('app', {
  // 状态
  state: () => ({
    loading: false, // 全局加载状态
    error: null // 全局错误信息
  }),

  // getters
  getters: {
    isLoading: (state) => state.loading,
    appError: (state) => state.error
  },

  // actions
  actions: {
    // 设置加载状态
    setLoading(status) {
      this.loading = status
    },
    
    // 设置错误信息
    setError(error) {
      this.error = error
    },
    
    // 清除错误信息
    clearError() {
      this.error = null
    },
    
    // 全局错误处理
    handleError(error) {
      console.error('全局错误:', error)
      this.setError(error.message || '发生错误')
    }
  }
})