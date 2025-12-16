import axios from './axios';
import { API_URL } from '../config';

const authService = {
    /**
     * 用户登录
     * @param {Object} credentials - 登录凭证
     * @param {string} credentials.username - 用户名
     * @param {string} credentials.password - 密码
     * @returns {Promise<Object>} 登录响应，包含 access_token 和 refresh_token
     */
    async login(credentials) {
        try {
            console.log('[AuthService] Login attempt:', credentials.username);
            const response = await axios.post(`${API_URL}/auth/login`, credentials);

            console.log('[AuthService] Login successful');

            // Store tokens
            if (response.access_token) {
                localStorage.setItem('access_token', response.access_token);
            }
            if (response.refresh_token) {
                localStorage.setItem('refresh_token', response.refresh_token);
            }
            if (response.user) {
                localStorage.setItem('username', response.user.username);
                localStorage.setItem('user_id', response.user.id);
            }

            return response;
        } catch (error) {
            console.error('[AuthService] Login failed:', error);
            throw error;
        }
    },

    /**
     * 用户注册
     * @param {Object} userData - 用户数据
     * @param {string} userData.username - 用户名
     * @param {string} userData.email - 邮箱
     * @param {string} userData.password - 密码
     * @returns {Promise<Object>} 注册响应
     */
    async register(userData) {
        try {
            console.log('[AuthService] Register attempt:', userData.username);
            const response = await axios.post(`${API_URL}/auth/register`, userData);

            console.log('[AuthService] Registration successful');

            // Auto login after registration
            if (response.access_token) {
                localStorage.setItem('access_token', response.access_token);
                localStorage.setItem('refresh_token', response.refresh_token);
                localStorage.setItem('username', response.user.username);
                localStorage.setItem('user_id', response.user.id);
            }

            return response;
        } catch (error) {
            console.error('[AuthService] Registration failed:', error);
            throw error;
        }
    },

    /**
     * 用户登出
     */
    logout() {
        console.log('[AuthService] Logging out');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
        localStorage.removeItem('user_id');
    },

    /**
     * 获取当前用户信息
     * @returns {Promise<Object>} 用户信息
     */
    async getCurrentUser() {
        try {
            const response = await axios.get(`${API_URL}/auth/me`);
            console.log('[AuthService] Get current user:', response);
            return response;
        } catch (error) {
            console.error('[AuthService] Get current user failed:', error);
            throw error;
        }
    },

    /**
     * 检查用户是否已登录
     * @returns {boolean} 是否已登录
     */
    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },

    /**
     * 获取存储的访问令牌
     * @returns {string|null} 访问令牌
     */
    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    /**
     * 获取存储的刷新令牌
     * @returns {string|null} 刷新令牌
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }
};

export default authService;
