<template>
    <div
        class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-purple-50 to-pink-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-4">
        <!-- Background decoration -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
            <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-400/20 rounded-full blur-3xl"></div>
            <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl"></div>
        </div>

        <!-- Register Card -->
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
                    <p class="text-gray-600 dark:text-gray-400 text-sm">创建新账户</p>
                </div>
            </template>

            <form @submit.prevent="handleRegister" class="space-y-4">
                <!-- Username -->
                <UFormGroup label="用户名" name="username" required>
                    <UInput v-model="form.username" icon="i-heroicons-user" placeholder="请输入用户名" size="lg"
                        :disabled="loading" />
                </UFormGroup>

                <!-- Email -->
                <UFormGroup label="邮箱" name="email" required>
                    <UInput v-model="form.email" type="email" icon="i-heroicons-envelope" placeholder="请输入邮箱" size="lg"
                        :disabled="loading" />
                </UFormGroup>

                <!-- Password -->
                <UFormGroup label="密码" name="password" required>
                    <UInput v-model="form.password" type="password" icon="i-heroicons-lock-closed"
                        placeholder="请输入密码（至少6位）" size="lg" :disabled="loading" />
                </UFormGroup>

                <!-- Confirm Password -->
                <UFormGroup label="确认密码" name="confirmPassword" required>
                    <UInput v-model="form.confirmPassword" type="password" icon="i-heroicons-lock-closed"
                        placeholder="请再次输入密码" size="lg" :disabled="loading" />
                </UFormGroup>

                <!-- Error message -->
                <div v-if="errorMessage"
                    class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
                    {{ errorMessage }}
                </div>

                <!-- Submit button -->
                <UButton type="submit" block size="lg" :loading="loading" :disabled="!isFormValid"
                    icon="i-heroicons-user-plus">
                    注册
                </UButton>

                <!-- Login link -->
                <div class="text-center text-sm text-gray-600 dark:text-gray-400">
                    已有账户？
                    <NuxtLink to="/login" class="text-primary-500 hover:text-primary-600 font-medium">
                        立即登录
                    </NuxtLink>
                </div>
            </form>
        </UCard>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/useAuth';

definePageMeta({
    layout: false
});

const router = useRouter();
const toast = useToast();
const { register } = useAuth();

const form = ref({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
});

const loading = ref(false);
const errorMessage = ref('');

const isFormValid = computed(() => {
    return form.value.username &&
        form.value.email &&
        form.value.password &&
        form.value.confirmPassword &&
        form.value.password === form.value.confirmPassword &&
        form.value.password.length >= 6;
});

const handleRegister = async () => {
    errorMessage.value = '';

    // Validate password match
    if (form.value.password !== form.value.confirmPassword) {
        errorMessage.value = '两次输入的密码不一致';
        return;
    }

    // Validate password length
    if (form.value.password.length < 6) {
        errorMessage.value = '密码长度至少为6位';
        return;
    }

    loading.value = true;

    try {
        await register({
            username: form.value.username,
            email: form.value.email,
            password: form.value.password
        });

        toast.add({
            title: '注册成功',
            description: `欢迎加入，${form.value.username}！`,
            icon: 'i-heroicons-check-circle',
            color: 'green'
        });

        // Redirect to home page
        router.push('/');
    } catch (error) {
        console.error('Registration failed:', error);
        errorMessage.value = error.message || '注册失败，请稍后重试';

        toast.add({
            title: '注册失败',
            description: errorMessage.value,
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        loading.value = false;
    }
};
</script>
