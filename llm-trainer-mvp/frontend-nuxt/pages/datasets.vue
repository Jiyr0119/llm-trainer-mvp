<template>
    <NuxtLayout name="default">
        <div class="container mx-auto px-4 py-8 max-w-7xl">
            <!-- Header -->
            <div class="flex items-center justify-between mb-8">
                <div>
                    <h1 class="text-3xl font-bold">数据集管理</h1>
                    <p class="text-gray-600 dark:text-gray-400 mt-2">上传和管理训练数据集</p>
                </div>
                <UButton icon="i-heroicons-plus" label="上传数据集" size="lg" @click="isUploadModalOpen = true" />
            </div>

            <!-- Upload Modal -->
            <UModal v-model="isUploadModalOpen">
                <UCard>
                    <template #header>
                        <h3 class="text-lg font-semibold">上传数据集</h3>
                    </template>

                    <form @submit.prevent="handleUpload" class="space-y-4">
                        <UFormGroup label="数据集名称" required>
                            <UInput v-model="uploadForm.name" placeholder="请输入数据集名称" />
                        </UFormGroup>

                        <UFormGroup label="选择文件" required>
                            <input type="file" accept=".csv" @change="handleFileChange"
                                class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100" />
                            <p class="text-xs text-gray-500 mt-2">请上传包含 text 和 label 列的 CSV 文件</p>
                        </UFormGroup>

                        <UFormGroup label="描述">
                            <UTextarea v-model="uploadForm.description" placeholder="数据集描述（可选）" :rows="3" />
                        </UFormGroup>

                        <div class="flex justify-end gap-2">
                            <UButton label="取消" variant="ghost" @click="isUploadModalOpen = false" />
                            <UButton type="submit" label="上传" :loading="uploading"
                                :disabled="!uploadForm.name || !uploadForm.file" />
                        </div>
                    </form>
                </UCard>
            </UModal>

            <!-- Datasets List -->
            <div v-if="loading" class="space-y-4">
                <USkeleton class="h-20 w-full" v-for="i in 3" :key="i" />
            </div>

            <div v-else-if="datasets.length === 0" class="text-center py-20">
                <UIcon name="i-heroicons-circle-stack"
                    class="w-20 h-20 text-gray-300 dark:text-gray-700 mx-auto mb-4" />
                <p class="text-gray-500 dark:text-gray-400 mb-4">还没有数据集</p>
                <UButton label="上传第一个数据集" icon="i-heroicons-plus" @click="isUploadModalOpen = true" />
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <UCard v-for="dataset in datasets" :key="dataset.id" class="hover:shadow-lg transition-shadow">
                    <div class="space-y-3">
                        <div class="flex items-start justify-between">
                            <div class="flex items-center gap-2">
                                <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary-500" />
                                <h3 class="font-semibold">{{ dataset.name }}</h3>
                            </div>
                            <UDropdown :items="getDatasetActions(dataset)">
                                <UButton icon="i-heroicons-ellipsis-vertical" variant="ghost" color="gray" square
                                    size="sm" />
                            </UDropdown>
                        </div>

                        <p v-if="dataset.description" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                            {{ dataset.description }}
                        </p>

                        <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                            <span>{{ dataset.rows || 0 }} 行</span>
                            <span>{{ formatDate(dataset.created_at) }}</span>
                        </div>
                    </div>
                </UCard>
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
const loading = ref(false);
const isUploadModalOpen = ref(false);
const uploading = ref(false);

const uploadForm = ref({
    name: '',
    description: '',
    file: null
});

const handleFileChange = (event) => {
    uploadForm.value.file = event.target.files[0];
};

const loadDatasets = async () => {
    loading.value = true;
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
        loading.value = false;
    }
};

const handleUpload = async () => {
    uploading.value = true;

    try {
        const formData = new FormData();
        formData.append('file', uploadForm.value.file);
        formData.append('name', uploadForm.value.name);
        if (uploadForm.value.description) {
            formData.append('description', uploadForm.value.description);
        }

        await axios.post(`${API_URL}/datasets/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        toast.add({
            title: '上传成功',
            description: '数据集已成功上传',
            icon: 'i-heroicons-check-circle',
            color: 'green'
        });

        isUploadModalOpen.value = false;
        uploadForm.value = { name: '', description: '', file: null };
        await loadDatasets();
    } catch (error) {
        console.error('Upload failed:', error);
        toast.add({
            title: '上传失败',
            description: error.message || '数据集上传失败',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        uploading.value = false;
    }
};

const deleteDataset = async (datasetId) => {
    try {
        await axios.delete(`${API_URL}/datasets/${datasetId}`);

        toast.add({
            title: '删除成功',
            description: '数据集已删除',
            icon: 'i-heroicons-check-circle',
            color: 'green'
        });

        await loadDatasets();
    } catch (error) {
        console.error('Delete failed:', error);
        toast.add({
            title: '删除失败',
            description: error.message || '无法删除数据集',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    }
};

const getDatasetActions = (dataset) => {
    return [[
        {
            label: '删除',
            icon: 'i-heroicons-trash',
            click: () => deleteDataset(dataset.id)
        }
    ]];
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
};

onMounted(() => {
    loadDatasets();
});
</script>
