<template>
    <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
        <!-- Navigation Bar -->
        <nav
            class="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex items-center justify-between h-16">
                    <!-- Logo & Brand -->
                    <div class="flex items-center gap-8">
                        <NuxtLink to="/" class="flex items-center gap-2 group">
                            <UIcon name="i-heroicons-sparkles" class="w-8 h-8 text-primary-500" />
                            <span
                                class="text-xl font-bold bg-gradient-to-r from-primary-500 to-purple-600 bg-clip-text text-transparent">
                                LLM Trainer
                            </span>
                        </NuxtLink>

                        <!-- Navigation Links -->
                        <div class="hidden md:flex items-center gap-1">
                            <UButton v-for="link in navLinks" :key="link.to" :to="link.to" :icon="link.icon"
                                :label="link.label" variant="ghost" color="gray"
                                :class="{ 'bg-gray-100 dark:bg-gray-800': isActive(link.to) }" />
                        </div>
                    </div>

                    <!-- User Menu -->
                    <div class="flex items-center gap-3">
                        <UButton icon="i-heroicons-moon" variant="ghost" color="gray" square @click="toggleDarkMode"
                            class="hidden sm:flex" />

                        <UDropdown :items="userMenuItems" :popper="{ placement: 'bottom-end' }">
                            <UButton icon="i-heroicons-user-circle" :label="user?.username || 'User'" variant="ghost"
                                color="gray" trailing-icon="i-heroicons-chevron-down" />
                        </UDropdown>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <main class="flex-1">
            <slot />
        </main>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const colorMode = useColorMode();

// Navigation links
const navLinks = [
    { to: '/', label: '首页', icon: 'i-heroicons-home' },
    { to: '/datasets', label: '数据集', icon: 'i-heroicons-circle-stack' },
    { to: '/training', label: '模型训练', icon: 'i-heroicons-cpu-chip' },
    { to: '/chat', label: 'AI 对话', icon: 'i-heroicons-chat-bubble-left-right' }
];

// User state (will be replaced with actual auth composable later)
const user = ref({
    username: localStorage.getItem('username') || '用户'
});

// User menu items
const userMenuItems = [
    [{
        label: user.value.username,
        slot: 'account',
        disabled: true
    }],
    [{
        label: '个人设置',
        icon: 'i-heroicons-cog-6-tooth',
        click: () => {
            // Navigate to settings
        }
    }],
    [{
        label: '退出登录',
        icon: 'i-heroicons-arrow-right-on-rectangle',
        click: handleLogout
    }]
];

// Check if route is active
const isActive = (path) => {
    if (path === '/') {
        return route.path === '/';
    }
    return route.path.startsWith(path);
};

// Toggle dark mode
const toggleDarkMode = () => {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark';
};

// Handle logout
function handleLogout() {
    // Clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');

    // Redirect to login
    router.push('/login');
}
</script>

<style scoped>
/* Additional scoped styles if needed */
</style>
