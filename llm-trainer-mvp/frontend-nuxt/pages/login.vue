<template>
    <div
        class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-purple-50 to-pink-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-4">
        <!-- Background decoration -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
            <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-400/20 rounded-full blur-3xl"></div>
            <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl"></div>
        </div>

        <!-- Login Card -->
        <UCard class="w-full max-w-md relative z-10 shadow-2xl">
            <template #header>
                <div class="text-center space-y-2">
                    <div class="flex justify-center">
                        <UIcon name="i-heroicons-sparkles" class="w-12 h-12 text-primary-500" />
                    </div>
                    <h1
                        class="text-2xl font-bold bg-gradient-to-r from-primary-500 to-purple-600 bg-clip-text text-transparent">
                        LLM Trainer
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400 text-sm">登录到您的账户</p>
                </div>
            </template>

            <form @submit.prevent="handleLogin" class="space-y-4">
                <!-- Username -->
                <UFormGroup label="用户名" name="username" required>
                    <UInput v-model="form.username" icon="i-heroicons-user" placeholder="请输入用户名" size="lg"
                        :disabled="loading" />
                </UFormGroup>

                <!-- Password -->
                <UFormGroup label="密码" name="password" required>
                    <UInput v-model="form.password" type="password" icon="i-heroicons-lock-closed" placeholder="请输入密码"
                        size="lg" :disabled="loading" />
                </UFormGroup>

                <!-- Error message -->
                <div v-if="errorMessage"
                    class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
                    {{ errorMessage }}
                </div>

                <!-- Submit button -->
                <UButton type="submit" block size="lg" :loading="loading" :disabled="!form.username || !form.password"
                    icon="i-heroicons-arrow-right-on-rectangle">
                    登录
                </UButton>

                <!-- Register link -->
                <div class="text-center text-sm text-gray-600 dark:text-gray-400">
                    还没有账户？
                    <NuxtLink to="/register" class="text-primary-500 hover:text-primary-600 font-medium">
                        立即注册
                    </NuxtLink>
                </div>
            </form>
        </UCard>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/useAuth';

definePageMeta({
    layout: false
});

const router = useRouter();
const toast = useToast();
const { login } = useAuth();

const form = ref({
    username: '',
    password: ''
});

const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
    errorMessage.value = '';
    loading.value = true;

    try {
        await login(form.value);

        toast.add({
            title: '登录成功',
            description: `欢迎回来，${form.value.username}！`,
            icon: 'i-heroicons-check-circle',
            color: 'green'
        });

        // Redirect to home page
        router.push('/');
    } catch (error) {
        console.error('Login failed:', error);
        errorMessage.value = error.message || '登录失败，请检查用户名和密码';

        toast.add({
            title: '登录失败',
            description: errorMessage.value,
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        loading.value = false;
    }
};
</script>
