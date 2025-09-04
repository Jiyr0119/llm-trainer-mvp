// 用户认证状态管理模块
import authService from '../../services/auth'

// 初始状态
const state = {
  token: authService.getAccessToken(), // 从本地存储获取token
  refreshToken: authService.getRefreshToken(), // 从本地存储获取刷新token
  user: null, // 当前用户信息
  loading: false, // 加载状态
  error: null // 错误信息
}

// getter函数，用于从state派生数据
const getters = {
  // 是否已登录
  isLoggedIn: state => !!state.token,
  // 当前用户
  currentUser: state => state.user,
  // 是否为管理员
  isAdmin: state => state.user && state.user.role === 'ADMIN',
  // 加载状态
  isLoading: state => state.loading,
  // 错误信息
  error: state => state.error
}

// 定义actions，用于执行异步操作
const actions = {
  // 注册用户
  async register({ commit }, userData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await authService.register(userData)
      commit('setLoading', false)
      return true
    } catch (error) {
      commit('setError', error.message || '注册失败')
      commit('setLoading', false)
      throw error
    }
  },

  // 用户登录
  async login({ commit, dispatch }, credentials) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const data = await authService.login(credentials)
      // 保存token到本地存储
      authService.saveTokens(data.access_token, data.refresh_token)
      // 更新状态
      commit('setToken', data.access_token)
      commit('setRefreshToken', data.refresh_token)
      // 获取用户信息
      await dispatch('fetchUserInfo')
      commit('setLoading', false)
      // 触发登录状态变化事件
      window.dispatchEvent(new Event('auth-state-changed'))
      return true
    } catch (error) {
      commit('setError', error.message || '登录失败')
      commit('setLoading', false)
      throw error
    }
  },

  // 获取用户信息
  async fetchUserInfo({ commit }) {
    commit('setLoading', true)
    try {
      const user = await authService.getCurrentUser()
      commit('setUser', user)
      commit('setLoading', false)
      return user
    } catch (error) {
      commit('setError', error.message || '获取用户信息失败')
      commit('setLoading', false)
      throw error
    }
  },

  // 刷新token
  async refreshToken({ commit, state }) {
    if (!state.refreshToken) {
      throw new Error('没有刷新令牌')
    }
    try {
      const data = await authService.refreshToken(state.refreshToken)
      // 保存新token
      authService.saveTokens(data.access_token, state.refreshToken)
      // 更新状态
      commit('setToken', data.access_token)
      return data.access_token
    } catch (error) {
      // 刷新失败，清除认证状态
      commit('clearAuth')
      throw error
    }
  },

  // 更新用户信息
  async updateUserInfo({ commit }, userData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const updatedUser = await authService.updateUserInfo(userData)
      commit('setUser', updatedUser)
      commit('setLoading', false)
      return updatedUser
    } catch (error) {
      commit('setError', error.message || '更新用户信息失败')
      commit('setLoading', false)
      throw error
    }
  },

  // 更新密码
  async updatePassword({ commit }, passwordData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await authService.updatePassword(passwordData)
      commit('setLoading', false)
      return true
    } catch (error) {
      commit('setError', error.message || '更新密码失败')
      commit('setLoading', false)
      throw error
    }
  },

  // 退出登录
  logout({ commit }) {
    // 清除本地存储中的token
    authService.clearTokens()
    // 清除状态
    commit('clearAuth')
    // 触发登录状态变化事件
    window.dispatchEvent(new Event('auth-state-changed'))
  }
}

// 定义mutations，用于修改状态
const mutations = {
  // 设置token
  setToken(state, token) {
    state.token = token
  },
  // 设置刷新token
  setRefreshToken(state, refreshToken) {
    state.refreshToken = refreshToken
  },
  // 设置用户信息
  setUser(state, user) {
    state.user = user
  },
  // 设置加载状态
  setLoading(state, status) {
    state.loading = status
  },
  // 设置错误信息
  setError(state, error) {
    state.error = error
  },
  // 清除错误信息
  clearError(state) {
    state.error = null
  },
  // 清除认证状态
  clearAuth(state) {
    state.token = null
    state.refreshToken = null
    state.user = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}