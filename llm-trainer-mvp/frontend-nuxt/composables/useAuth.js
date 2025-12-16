import { ref, computed } from 'vue';
import authService from '~/services/authService';

// Global auth state
const user = ref(null);
const isAuthenticated = ref(false);

export const useAuth = () => {
    // Initialize auth state from localStorage
    const initAuth = () => {
        if (process.client) {
            const token = authService.getAccessToken();
            isAuthenticated.value = !!token;

            if (token) {
                const username = localStorage.getItem('username');
                const userId = localStorage.getItem('user_id');
                user.value = {
                    id: userId,
                    username: username
                };
            }
        }
    };

    // Login
    const login = async (credentials) => {
        try {
            const response = await authService.login(credentials);
            isAuthenticated.value = true;
            user.value = response.user;
            return response;
        } catch (error) {
            isAuthenticated.value = false;
            user.value = null;
            throw error;
        }
    };

    // Register
    const register = async (userData) => {
        try {
            const response = await authService.register(userData);
            isAuthenticated.value = true;
            user.value = response.user;
            return response;
        } catch (error) {
            isAuthenticated.value = false;
            user.value = null;
            throw error;
        }
    };

    // Logout
    const logout = () => {
        authService.logout();
        isAuthenticated.value = false;
        user.value = null;
    };

    // Refresh user data
    const refreshUser = async () => {
        try {
            const response = await authService.getCurrentUser();
            user.value = response;
            return response;
        } catch (error) {
            console.error('Failed to refresh user:', error);
            logout();
            throw error;
        }
    };

    // Initialize on composable creation
    initAuth();

    return {
        user: computed(() => user.value),
        isAuthenticated: computed(() => isAuthenticated.value),
        login,
        register,
        logout,
        refreshUser
    };
};
