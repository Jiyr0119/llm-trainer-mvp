// 用户认证状态管理 - Pinia版本
import { defineStore } from 'pinia'
import authService from '../services/auth'

// 定义auth存储
export const useAuthStore = defineStore('auth', {
  // 状态
  state: () => ({
    token: authService.getAccessToken(), // 从本地存储获取token
    refreshToken: authService.getRefreshToken(), // 从本地存储获取刷新token
    user: null, // 当前用户信息
    loading: false, // 加载状态
    error: null // 错误信息
  }),

  // getters，类似于Vuex的getters和计算属性
  getters: {
    // 是否已登录
    isLoggedIn: (state) => !!state.token,
    // 当前用户
    currentUser: (state) => state.user,
    // 是否为管理员
    isAdmin: (state) => state.user && state.user.role === 'ADMIN',
    // 加载状态
    isLoading: (state) => state.loading,
    // 错误信息
    authError: (state) => state.error
  },

  // actions，类似于Vuex的actions和mutations的组合
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

    // 设置token
    setToken(token) {
      this.token = token
    },

    // 设置刷新token
    setRefreshToken(refreshToken) {
      this.refreshToken = refreshToken
    },

    // 设置用户信息
    setUser(user) {
      this.user = user
    },

    // 清除认证状态
    clearAuth() {
      this.token = null
      this.refreshToken = null
      this.user = null
    },

    // 注册用户
    async register(userData) {
      this.setLoading(true)
      this.clearError()
      try {
        await authService.register(userData)
        this.setLoading(false)
        return true
      } catch (error) {
        this.setError(error.message || '注册失败')
        this.setLoading(false)
        throw error
      }
    },

    // 用户登录
    async login(credentials) {
      this.setLoading(true)
      this.clearError()
      try {
        const data = await authService.login(credentials)
        // 保存token到本地存储
        authService.saveTokens(data.access_token, data.refresh_token)
        // 更新状态
        this.setToken(data.access_token)
        this.setRefreshToken(data.refresh_token)
        // 获取用户信息
        await this.fetchUserInfo()
        this.setLoading(false)
        // 触发登录状态变化事件
        window.dispatchEvent(new Event('auth-state-changed'))
        return true
      } catch (error) {
        this.setError(error.message || '登录失败')
        this.setLoading(false)
        throw error
      }
    },

    // 获取用户信息
    async fetchUserInfo() {
      this.setLoading(true)
      try {
        const user = await authService.getCurrentUser()
        this.setUser(user)
        this.setLoading(false)
        return user
      } catch (error) {
        this.setError(error.message || '获取用户信息失败')
        this.setLoading(false)
        throw error
      }
    },

    // 刷新token
    async refreshToken() {
      if (!this.refreshToken) {
        throw new Error('没有刷新令牌')
      }
      try {
        const data = await authService.refreshToken(this.refreshToken)
        // 保存新token
        authService.saveTokens(data.access_token, this.refreshToken)
        // 更新状态
        this.setToken(data.access_token)
        return data.access_token
      } catch (error) {
        // 刷新失败，清除认证状态
        this.clearAuth()
        throw error
      }
    },

    // 更新用户信息
    async updateUserInfo(userData) {
      this.setLoading(true)
      this.clearError()
      try {
        const updatedUser = await authService.updateUserInfo(userData)
        this.setUser(updatedUser)
        this.setLoading(false)
        return updatedUser
      } catch (error) {
        this.setError(error.message || '更新用户信息失败')
        this.setLoading(false)
        throw error
      }
    },

    // 更新密码
    async updatePassword(passwordData) {
      this.setLoading(true)
      this.clearError()
      try {
        await authService.updatePassword(passwordData)
        this.setLoading(false)
        return true
      } catch (error) {
        this.setError(error.message || '更新密码失败')
        this.setLoading(false)
        throw error
      }
    },

    // 退出登录
    logout() {
      // 清除本地存储中的token
      authService.clearTokens()
      // 清除状态
      this.clearAuth()
      // 触发登录状态变化事件
      window.dispatchEvent(new Event('auth-state-changed'))
    }
  }
})