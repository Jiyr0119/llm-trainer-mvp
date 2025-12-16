<template>
    <NuxtLayout name="default">
        <div class="min-h-screen">
            <!-- Hero Section -->
            <section class="relative py-20 px-4 overflow-hidden">
                <!-- Gradient Background -->
                <div
                    class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-purple-500/10 to-pink-500/10 dark:from-primary-900/20 dark:via-purple-900/20 dark:to-pink-900/20">
                </div>

                <!-- Animated blobs -->
                <div class="absolute top-20 left-20 w-72 h-72 bg-primary-400/30 rounded-full blur-3xl animate-pulse">
                </div>
                <div
                    class="absolute bottom-20 right-20 w-96 h-96 bg-purple-400/30 rounded-full blur-3xl animate-pulse delay-1000">
                </div>

                <div class="max-w-7xl mx-auto relative z-10">
                    <div class="text-center space-y-8">
                        <!-- Icon -->
                        <div class="flex justify-center">
                            <div class="p-4 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl shadow-2xl">
                                <UIcon name="i-heroicons-sparkles" class="w-16 h-16 text-white" />
                            </div>
                        </div>

                        <!-- Title -->
                        <h1 class="text-5xl md:text-6xl font-bold">
                            <span
                                class="bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                                大语言模型训练平台
                            </span>
                        </h1>

                        <!-- Subtitle -->
                        <p class="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                            轻松管理数据集，训练定制模型，体验智能对话
                        </p>

                        <!-- Quick Actions -->
                        <div class="flex flex-wrap gap-4 justify-center">
                            <UButton to="/chat" size="xl" icon="i-heroicons-chat-bubble-left-right" label="开始对话"
                                color="primary" variant="solid" class="shadow-lg hover:shadow-xl transition-shadow" />
                            <UButton to="/datasets" size="xl" icon="i-heroicons-circle-stack" label="管理数据集" color="gray"
                                variant="outline" />
                        </div>

                        <!-- Stats -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto pt-12">
                            <div class="text-center">
                                <div class="text-4xl font-bold text-primary-600 dark:text-primary-400">{{ stats.datasets
                                    }}</div>
                                <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">数据集</div>
                            </div>
                            <div class="text-center">
                                <div class="text-4xl font-bold text-purple-600 dark:text-purple-400">{{ stats.models }}
                                </div>
                                <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">可用模型</div>
                            </div>
                            <div class="text-center">
                                <div class="text-4xl font-bold text-pink-600 dark:text-pink-400">{{ stats.conversations
                                    }}</div>
                                <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">对话历史</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Features Grid -->
            <section class="py-20 px-4 bg-white dark:bg-gray-900">
                <div class="max-w-7xl mx-auto">
                    <h2 class="text-3xl font-bold text-center mb-12">核心功能</h2>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <!-- Feature Card: Datasets -->
                        <UCard class="group hover:shadow-2xl transition-all duration-300 cursor-pointer"
                            @click="navigateTo('/datasets')">
                            <div class="space-y-4">
                                <div
                                    class="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <UIcon name="i-heroicons-circle-stack" class="w-6 h-6 text-white" />
                                </div>
                                <h3 class="text-xl font-semibold">数据集管理</h3>
                                <p class="text-gray-600 dark:text-gray-400">
                                    上传、管理和预览训练数据集，支持CSV格式，轻松组织训练数据
                                </p>
                                <div class="flex items-center text-primary-600 dark:text-primary-400 font-medium">
                                    查看详情
                                    <UIcon name="i-heroicons-arrow-right"
                                        class="ml-1 group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </UCard>

                        <!-- Feature Card: Training -->
                        <UCard class="group hover:shadow-2xl transition-all duration-300 cursor-pointer"
                            @click="navigateTo('/training')">
                            <div class="space-y-4">
                                <div
                                    class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <UIcon name="i-heroicons-cpu-chip" class="w-6 h-6 text-white" />
                                </div>
                                <h3 class="text-xl font-semibold">模型训练</h3>
                                <p class="text-gray-600 dark:text-gray-400">
                                    选择数据集，配置参数，训练定制化的语言模型，实时查看训练进度
                                </p>
                                <div class="flex items-center text-primary-600 dark:text-primary-400 font-medium">
                                    开始训练
                                    <UIcon name="i-heroicons-arrow-right"
                                        class="ml-1 group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </UCard>

                        <!-- Feature Card: AI Chat -->
                        <UCard class="group hover:shadow-2xl transition-all duration-300 cursor-pointer"
                            @click="navigateTo('/chat')">
                            <div class="space-y-4">
                                <div
                                    class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <UIcon name="i-heroicons-chat-bubble-left-right" class="w-6 h-6 text-white" />
                                </div>
                                <h3 class="text-xl font-semibold">AI 对话</h3>
                                <p class="text-gray-600 dark:text-gray-400">
                                    与训练好的模型对话，支持多模型切换，流式响应，保存对话历史
                                </p>
                                <div class="flex items-center text-primary-600 dark:text-primary-400 font-medium">
                                    开始对话
                                    <UIcon name="i-heroicons-arrow-right"
                                        class="ml-1 group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </UCard>
                    </div>
                </div>
            </section>

            <!-- Getting Started -->
            <section class="py-20 px-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950">
                <div class="max-w-5xl mx-auto">
                    <h2 class="text-3xl font-bold text-center mb-12">快速开始</h2>

                    <div class="space-y-8">
                        <div class="flex gap-4 items-start">
                            <div
                                class="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
                                1
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold mb-2">上传数据集</h3>
                                <p class="text-gray-600 dark:text-gray-400">
                                    在"数据集管理"页面上传包含 text 和 label 列的 CSV 文件
                                </p>
                            </div>
                        </div>

                        <div class="flex gap-4 items-start">
                            <div
                                class="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
                                2
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold mb-2">训练模型</h3>
                                <p class="text-gray-600 dark:text-gray-400">
                                    选择数据集，设置训练参数（epochs、batch size等），开始训练
                                </p>
                            </div>
                        </div>

                        <div class="flex gap-4 items-start">
                            <div
                                class="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
                                3
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold mb-2">测试对话</h3>
                                <p class="text-gray-600 dark:text-gray-400">
                                    训练完成后，在"AI 对话"页面与模型交互，体验智能对话
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { navigateTo } from '#app';

definePageMeta({
    middleware: 'auth'
});

const stats = ref({
    datasets: 0,
    models: 0,
    conversations: 0
});

onMounted(async () => {
    // Load stats from APIs
    // For now, use placeholder values
    stats.value = {
        datasets: 0,
        models: 3,
        conversations: 0
    };
});
</script>
