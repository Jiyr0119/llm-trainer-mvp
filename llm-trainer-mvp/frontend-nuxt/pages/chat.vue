<template>
    <NuxtLayout name="default">
        <div class="flex h-[calc(100vh-4rem)] relative">
            <!-- Sidebar -->
            <div class="border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 transition-all duration-300 ease-in-out flex flex-col"
                :class="[isSidebarOpen ? 'w-64' : 'w-0 overflow-hidden md:w-16']">
                <!-- Sidebar Header -->
                <div class="p-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                    <UButton v-if="isSidebarOpen" block color="primary" variant="solid" icon="i-heroicons-plus"
                        class="flex-1 mr-2" @click="createNewConversation">
                        New Chat
                    </UButton>
                    <UButton v-else icon="i-heroicons-plus" color="primary" variant="ghost" square
                        @click="createNewConversation" />

                    <!-- Toggle button (only visible on mobile or when open? simplified for now) -->
                </div>

                <!-- History List -->
                <div class="flex-1 overflow-y-auto p-2" v-if="isSidebarOpen">
                    <div v-if="loadingConversations" class="space-y-2">
                        <USkeleton class="h-10 w-full" v-for="i in 5" :key="i" />
                    </div>
                    <div v-else class="space-y-1">
                        <UButton v-for="conv in conversations" :key="conv.id" :label="conv.title || 'New Chat'"
                            :variant="currentConversationId === conv.id ? 'soft' : 'ghost'" color="gray" block
                            class="justify-start text-left truncate" @click="loadConversation(conv.id)">
                            <template #leading>
                                <UIcon name="i-heroicons-chat-bubble-left" />
                            </template>
                        </UButton>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="p-4 border-t border-gray-100 dark:border-gray-800">
                    <UButton v-if="isSidebarOpen" icon="i-heroicons-cog-6-tooth" label="Settings" variant="ghost"
                        color="gray" block class="justify-start" />
                    <UButton v-else icon="i-heroicons-cog-6-tooth" variant="ghost" square />
                </div>
            </div>

            <!-- Main Chat Area -->
            <div class="flex-1 flex flex-col h-full bg-white dark:bg-gray-950 relative">
                <!-- Top Bar -->
                <div class="h-14 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4">
                    <div class="flex items-center gap-2">
                        <UButton icon="i-heroicons-bars-3" color="gray" variant="ghost" @click="toggleSidebar"
                            class="md:hidden" />
                        <div class="font-medium">
                            {{ currentConversation ? currentConversation.title : 'New Chat' }}
                        </div>
                    </div>

                    <div>
                        <USelectMenu v-model="selectedModel" :options="models" placeholder="Select Model"
                            option-attribute="id" />
                    </div>
                </div>

                <!-- Messages Area -->
                <div class="flex-1 overflow-y-auto p-4 space-y-6" ref="messagesContainer">
                    <div v-if="messages.length === 0"
                        class="flex flex-col items-center justify-center h-full text-gray-500">
                        <UIcon name="i-heroicons-sparkles" class="w-16 h-16 mb-4 text-primary-500" />
                        <h2 class="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-2">How can I help you
                            today?
                        </h2>
                        <p class="text-sm">Select a model and start typing...</p>
                    </div>

                    <div v-for="(msg, idx) in messages" :key="idx" class="flex gap-4 max-w-4xl mx-auto"
                        :class="[msg.role === 'user' ? 'flex-row-reverse' : '']">
                        <!-- Avatar -->
                        <UAvatar
                            :src="msg.role === 'user' ? 'https://avatars.githubusercontent.com/u/739984?v=4' : 'https://avatars.githubusercontent.com/u/475315?v=4'"
                            :alt="msg.role" size="sm" class="mt-1" />

                        <!-- Bubble -->
                        <div class="group relative px-4 py-3 rounded-2xl max-w-[85%]" :class="[
                            msg.role === 'user'
                                ? 'bg-primary-500 text-white rounded-br-none'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-100 rounded-bl-none'
                        ]">
                            <!-- Content (Markdown to be added) -->
                            <div class="prose dark:prose-invert max-w-none text-sm leading-relaxed whitespace-pre-wrap">
                                {{ msg.content }}
                            </div>
                            <!-- Loading Indicator for streaming -->
                            <span v-if="msg.isStreaming"
                                class="inline-block w-2 h-4 ml-1 bg-current animate-pulse"></span>
                        </div>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="p-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
                    <div class="max-w-4xl mx-auto relative cursor-text">
                        <UTextarea v-model="userInput" :rows="1" autoresize :maxrows="5" placeholder="Message..."
                            class="w-full" :ui="{
                                padding: { sm: 'pr-12' },
                                color: { gray: { outline: 'ring-1 ring-gray-300 dark:ring-gray-700 focus:ring-2 focus:ring-primary-500' } }
                            }" @keydown.enter.prevent="handleEnter" />

                        <div class="absolute bottom-1.5 right-2">
                            <UButton :loading="isSending" :disabled="!userInput.trim() || isSending"
                                icon="i-heroicons-paper-airplane" size="sm" color="primary" variant="solid" square
                                @click="sendMessage" />
                        </div>
                    </div>
                    <div class="text-center text-xs text-gray-400 mt-2">
                        AI can make mistakes. Consider checking important information.
                    </div>
                </div>
            </div>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import chatService from '~/services/chatService';

definePageMeta({
    middleware: 'auth'
});

const toast = useToast();

const isSidebarOpen = ref(true);
const toggleSidebar = () => isSidebarOpen.value = !isSidebarOpen.value;

const loadingConversations = ref(false);
const conversations = ref([]);
const currentConversationId = ref(null);
const currentConversation = ref(null);

const messages = ref([]);
const userInput = ref('');
const isSending = ref(false);
const messagesContainer = ref(null);

const models = ref(['gpt-3.5-turbo', 'gpt-4', 'claude-3-opus', 'gemini-pro']); // Placeholder
const selectedModel = ref('gpt-3.5-turbo');

// Functions
const scrollToBottom = async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
};

const loadConversations = async () => {
    loadingConversations.value = true;
    try {
        const list = await chatService.getConversations();
        conversations.value = list;
    } catch (e) {
        console.error(e);
        toast.add({
            title: '加载失败',
            description: '无法加载对话历史',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        loadingConversations.value = false;
    }
};

const createNewConversation = () => {
    currentConversationId.value = null;
    currentConversation.value = null;
    messages.value = [];
    // Logic to create a new ID when sending message or now
};

const loadConversation = async (id) => {
    if (currentConversationId.value === id) return;
    currentConversationId.value = id;

    // Find title
    const conv = conversations.value.find(c => c.id === id);
    if (conv) currentConversation.value = conv;

    try {
        const msgs = await chatService.getConversationMessages(id);
        messages.value = msgs.map(m => ({ ...m, role: m.role || 'assistant', content: m.content || '' })); // normalization
        scrollToBottom();
    } catch (e) {
        console.error(e);
        toast.add({
            title: '加载失败',
            description: '无法加载对话消息',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    }
};

const sendMessage = async () => {
    const content = userInput.value.trim();
    if (!content) return;

    // User Message
    messages.value.push({ role: 'user', content });
    userInput.value = '';
    isSending.value = true;

    // Assistant Placeholder
    const assistantMsg = { role: 'assistant', content: '', isStreaming: true };
    messages.value.push(assistantMsg);

    scrollToBottom();

    try {
        // Prepare context
        // If new conversation, create it first? Or let backend handle it?
        // Existing logic usually requires conversation ID or creates one. 
        // For MVP refactor, assuming simple /completions call is stateless or we handle state.
        // chatService.sendMessage expects { model, messages, stream: true }

        // TODO: Handle conversation ID creation if null

        await chatService.sendMessage({
            model: selectedModel.value,
            messages: messages.value.slice(0, -1), // Exclude the empty assistant placeholder
            stream: true
        }, (chunk, fullText) => {
            assistantMsg.content = fullText;
            scrollToBottom();
        });

    } catch (e) {
        assistantMsg.content = `Error: ${e.message}`;
        toast.add({
            title: '发送失败',
            description: e.message || '消息发送失败，请重试',
            icon: 'i-heroicons-x-circle',
            color: 'red'
        });
    } finally {
        isSending.value = false;
        assistantMsg.isStreaming = false;
    }
};

const handleEnter = (e) => {
    if (!e.shiftKey) {
        sendMessage();
    }
};

onMounted(() => {
    loadConversations();
    // Load models
    chatService.getModels().then(m => {
        if (m && m.length) {
            models.value = m.map(x => x.id);
            selectedModel.value = models.value[0];
        }
    }).catch(e => console.error(e));
});
</script>
