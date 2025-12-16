<template>
    <NuxtLayout name="default">
        <div class="container mx-auto px-4 py-8 max-w-7xl">
            <!-- Header -->
            <div class="mb-8">
                <h1 class="text-3xl font-bold">模型训练</h1>
                <p class="text-gray-600 dark:text-gray-400 mt-2">配置参数并开始训练模型</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Training Form -->
                <div class="lg:col-span-2">
                    <UCard>
                        <template #header>
                            <h2 class="text-xl font-semibold">训练配置</h2>
                        </template>

                        <form @submit.prevent="handleStartTraining" class="space-y-6">
                            <!-- Dataset Selection -->
                            <UFormGroup label="选择数据集" required>
                                <USelectMenu v-model="trainingForm.dataset" :options="datasets" placeholder="请选择数据集"
                                    option-attribute="name" value-attribute="id" :loading="loadingDatasets">
                                    <template #label>
                                        <span v-if="trainingForm.dataset">{{ trainingForm.dataset.name }}</span>
                                        <span v-else class="text-gray-400">请选择数据集</span>
                                    </template>
                                </USelectMenu>
                            </UFormGroup>

                            <!-- Model Name -->
                            <UFormGroup label="模型名称" required>
                                <UInput v-model="trainingForm.modelName" placeholder="例如: my-custom-model" />
                            </UFormGroup>

                            <!-- Training Parameters -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <UFormGroup label="Epochs" required>
                                    <UInput v-model.number="trainingForm.epochs" type="number" min="1" max="100"
                                        placeholder="3" />
                                </UFormGroup>

                                <UFormGroup label="Batch Size" required>
                                    <UInput v-model.number="trainingForm.batchSize" type="number" min="1" max="128"
                                        placeholder="16" />
                                </UFormGroup>

                                <UFormGroup label="Learning Rate">
                                    <UInput v-model.number="trainingForm.learningRate" type="number" step="0.00001"
                                        placeholder="0.00002" />
                                </UFormGroup>

                                <UFormGroup label="Max Length">
                                    <UInput v-model.number="trainingForm.maxLength" type="number" min="1"
                                        placeholder="128" />
                                </UFormGroup>
                            </div>

                            <!-- Submit Button -->
                            <div class="flex gap-3">
                                <UButton type="submit" size="lg" icon="i-heroicons-play" :loading="training"
                                    :disabled="!trainingForm.dataset || !trainingForm.modelName">
                                    开始训练
                                </UButton>
                                <UButton type="button" variant="ghost" size="lg" @click="resetForm">
                                    重置
                                </UButton>
                            </div>
                        </form>
                    </UCard>
                </div>

                <!-- Training History -->
                <div class="lg:col-span-1">
                    <UCard>
                        <template #header>
                            <h2 class="text-xl font-semibold">训练历史</h2>
                        </template>

                        <div v-if="loadingHistory" class="space-y-3">
                            <USkeleton class="h-16 w-full" v-for="i in 3" :key="i" />
                        </div>

                        <div v-else-if="trainingHistory.length === 0"
                            class="text-center py-8 text-gray-500 dark:text-gray-400">
                            <UIcon name="i-heroicons-clock" class="w-12 h-12 mx-auto mb-2 opacity-50" />
                            <p class="text-sm">暂无训练历史</p>
                        </div>

                        <div v-else class="space-y-3 max-h-[500px] overflow-y-auto">
                            <div v-for="item in trainingHistory" :key="item.id"
                                class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                                <div class="flex items-start justify-between mb-2">
                                    <h4 class="font-medium text-sm">{{ item.model_name }}</h4>
                                    <UBadge :color="getStatusColor(item.status)" :label="getStatusLabel(item.status)"
                                        size="xs" />
                                </div>
                                <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                                    <div>数据集: {{ item.dataset_name || 'N/A' }}</div>
                                    <div>{{ formatDate(item.created_at) }}</div>
                                </div>
                            </div>
                        </div>
                    </UCard>
                </div>
            </div>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '~/services/axios';
import { API_URL } from '~/config';

definePageMeta({
    middleware: 'auth'
});

const toast = useToast();

const datasets = ref([]);
const loadingDatasets = ref(false);

const trainingHistory = ref([]);
const loadingHistory = ref(false);

const training = ref(false);

const trainingForm = ref({
    dataset: null,
    modelName: '',
    epochs: 3,
    batchSize: 16,
    learningRate: 0.00002,
    maxLength: 128
});

const loadDatasets = async () => {
    loadingDatasets.value = true;
    try {
        const response = await axios.get(`${API_URL}/datasets`);
        datasets.value = response.datasets || response || [];
    } catch (error) {
        console.error('Failed to load datasets:', error);
        toast.add({
            title: '加载失败',
            description: '无法加载数据集列表',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        loadingDatasets.value = false;
    }
};

const loadTrainingHistory = async () => {
    loadingHistory.value = true;
    try {
        const response = await axios.get(`${API_URL}/training/jobs`);
        trainingHistory.value = response.jobs || response || [];
    } catch (error) {
        console.error('Failed to load training history:', error);
    } finally {
        loadingHistory.value = false;
    }
};

const handleStartTraining = async () => {
    training.value = true;

    try {
        const payload = {
            dataset_id: trainingForm.value.dataset.id,
            model_name: trainingForm.value.modelName,
            epochs: trainingForm.value.epochs,
            batch_size: trainingForm.value.batchSize,
            learning_rate: trainingForm.value.learningRate,
            max_length: trainingForm.value.maxLength
        };

        await axios.post(`${API_URL}/training/start`, payload);

        toast.add({
            title: '训练已启动',
            description: `模型 ${trainingForm.value.modelName} 开始训练`,
            icon: 'i-heroicons-check-circle',
            color: 'green'
        });

        // Reload history
        await loadTrainingHistory();

        // Reset form
        resetForm();
    } catch (error) {
        console.error('Training failed:', error);
        toast.add({
            title: '训练失败',
            description: error.message || '无法启动训练',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        training.value = false;
    }
};

const resetForm = () => {
    trainingForm.value = {
        dataset: null,
        modelName: '',
        epochs: 3,
        batchSize: 16,
        learningRate: 0.00002,
        maxLength: 128
    };
};

const getStatusColor = (status) => {
    const colorMap = {
        'pending': 'yellow',
        'running': 'blue',
        'completed': 'green',
        'failed': 'red'
    };
    return colorMap[status] || 'gray';
};

const getStatusLabel = (status) => {
    const labelMap = {
        'pending': '等待中',
        'running': '训练中',
        'completed': '已完成',
        'failed': '失败'
    };
    return labelMap[status] || status;
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
};

onMounted(() => {
    loadDatasets();
    loadTrainingHistory();
});
</script>
