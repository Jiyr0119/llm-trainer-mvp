<template>
  <div class="gemini-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <el-button class="new-chat-btn" @click="createNewConversation" v-if="!isSidebarCollapsed">
          <el-icon class="icon">
            <Plus />
          </el-icon>
          <span>New chat</span>
        </el-button>
        <el-button class="collapse-btn" @click="toggleSidebar" circle text>
          <el-icon>
            <component :is="isSidebarCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
        </el-button>
      </div>

      <div class="sidebar-content" v-show="!isSidebarCollapsed">
        <div class="history-section">
          <div class="section-title">Recent</div>
          <el-scrollbar>
            <div v-for="conv in conversations" :key="conv.id" class="history-item"
              :class="{ active: currentConversation?.id === conv.id }" @click="selectConversation(conv)">
              <el-icon class="item-icon">
                <ChatDotRound />
              </el-icon>
              <span class="item-title">{{ conv.title || 'New Conversation' }}</span>

              <el-dropdown trigger="click" @command="handleConvAction($event, conv)" class="item-actions">
                <el-icon class="more-icon">
                  <MoreFilled />
                </el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="rename">Rename</el-dropdown-item>
                    <el-dropdown-item command="delete" divided class="text-danger">Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-scrollbar>
        </div>
      </div>

      <!-- Collapsed New Chat Button -->
      <div class="collapsed-actions" v-show="isSidebarCollapsed">
        <el-tooltip content="New chat" placement="right">
          <el-button class="collapsed-new-btn" @click="createNewConversation" circle>
            <el-icon>
              <Plus />
            </el-icon>
          </el-button>
        </el-tooltip>
      </div>

      <div class="sidebar-footer" v-if="!isSidebarCollapsed">
        <div class="user-profile">
          <!-- Placeholder for user settings or profile -->
          <el-button text @click="showSettings = true">
            <el-icon>
              <Setting />
            </el-icon> Settings
          </el-button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar (Mobile/Model Select) -->
      <div class="top-bar">
        <div class="model-selector">
          <el-dropdown trigger="click" @command="handleModelChange">
            <span class="model-trigger">
              {{ currentModelName }} <el-icon>
                <ArrowDown />
              </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="model in availableModels" :key="model.id" :command="model.id"
                  :class="{ active: selectedModel === model.id }">
                  <div class="model-item">
                    <span class="name">{{ model.name }}</span>
                    <span class="desc">{{ model.description }}</span>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- Chat Area -->
      <div class="chat-scroll-area" ref="messageScrollbar">
        <div class="chat-wrapper">
          <!-- Welcome Screen -->
          <div v-if="messages.length === 0" class="welcome-screen">
            <div class="greeting">
              <h1>Hello, User</h1>
              <p>How can I help you today?</p>
            </div>
            <div class="suggestion-chips">
              <div class="chip" @click="fillInput('Explain quantum computing in simple terms')">
                <el-icon>
                  <Lightning />
                </el-icon>
                <span>Explain quantum computing</span>
              </div>
              <div class="chip" @click="fillInput('Write a python script to parse CSV')">
                <el-icon>
                  <Monitor />
                </el-icon>
                <span>Python CSV script</span>
              </div>
              <div class="chip" @click="fillInput('Draft an email for a sick leave')">
                <el-icon>
                  <Message />
                </el-icon>
                <span>Sick leave email</span>
              </div>
            </div>
          </div>

          <!-- Message List -->
          <div v-else class="message-list">
            <div v-for="(message, index) in messages" :key="index" class="message-row" :class="message.role">
              <div class="message-avatar">
                <el-avatar :size="32" :icon="message.role === 'user' ? UserFilled : Service" :class="message.role" />
              </div>
              <div class="message-content-wrapper">
                <div class="message-sender">{{ message.role === 'user' ? 'You' : 'Assistant' }}</div>
                <div class="message-bubble" :class="{ 'error': message.error }">
                  <div v-if="message.role === 'assistant' && message.loading" class="typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                  <div v-else class="markdown-body" v-html="renderMarkdown(message.content)"></div>
                </div>
                <div v-if="message.role === 'assistant' && !message.loading && !message.error" class="message-actions">
                  <el-tooltip content="Copy" placement="bottom">
                    <el-icon class="action-icon" @click="copyToClipboard(message.content)">
                      <CopyDocument />
                    </el-icon>
                  </el-tooltip>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-container">
        <div class="input-box">
          <el-input v-model="userInput" type="textarea" :autosize="{ minRows: 1, maxRows: 6 }"
            placeholder="Enter a prompt here" resize="none" class="chat-input"
            @keydown.enter.exact.prevent="sendMessage" />
          <div class="input-actions">
            <el-button type="primary" circle :disabled="!userInput.trim() || isGenerating" @click="sendMessage">
              <el-icon>
                <Position />
              </el-icon>
            </el-button>
          </div>
        </div>
        <div class="disclaimer">
          AI can make mistakes. Consider checking important information.
        </div>
      </div>
    </main>

    <!-- Dialogs -->
    <el-dialog v-model="showSettings" title="Settings" width="400px" append-to-body>
      <el-form label-position="top">
        <el-form-item label="Temperature">
          <el-slider v-model="modelSettings.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="Max Length">
          <el-slider v-model="modelSettings.max_tokens" :min="100" :max="4096" :step="100" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSettings = false">Cancel</el-button>
          <el-button type="primary" @click="saveSettings">Save</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="showRenameDialog" title="Rename Chat" width="400px" append-to-body>
      <el-input v-model="newConversationTitle" placeholder="Chat name" @keydown.enter="renameConversation" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRenameDialog = false">Cancel</el-button>
          <el-button type="primary" @click="renameConversation">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import {
  Plus, ChatDotRound, MoreFilled, Expand, Fold, Setting,
  ArrowDown, UserFilled, Service, Position, Lightning, Monitor, Message, CopyDocument
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css'; // Or github-dark.css for dark mode if implemented
import chatService from '../services/chatService';

// --- Markdown Setup ---
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true
});

// --- State ---
const isSidebarCollapsed = ref(false);
const conversations = ref([]);
const currentConversation = ref(null);
const messages = ref([]);
const userInput = ref('');
const isGenerating = ref(false);
const messageScrollbar = ref(null);

const availableModels = ref([]);
const selectedModel = ref('');
const modelSettings = ref({ temperature: 0.7, max_tokens: 2048 });

const showSettings = ref(false);
const showRenameDialog = ref(false);
const newConversationTitle = ref('');
const conversationToRename = ref(null);

// --- Computed ---
const currentModelName = computed(() => {
  const model = availableModels.value.find(m => m.id === selectedModel.value);
  return model ? model.name : 'Select Model';
});

// --- Lifecycle ---
onMounted(async () => {
  try {
    const models = await chatService.getModels();
    availableModels.value = models;
    if (models.length > 0) selectedModel.value = models[0].id;

    const convs = await chatService.getConversations();
    conversations.value = convs;

    // Do NOT auto-select last conversation for a "fresh" feel, or do it if preferred.
    // Let's auto-select for continuity.
    if (convs.length > 0) {
      selectConversation(convs[0]);
    } else {
      createNewConversation();
    }
  } catch (error) {
    ElMessage.error('Failed to initialize: ' + error.message);
  }
});

// Auto-scroll
watch(messages, () => {
  scrollToBottom();
}, { deep: true });

const scrollToBottom = async () => {
  await nextTick();
  if (messageScrollbar.value) {
    messageScrollbar.value.scrollTop = messageScrollbar.value.scrollHeight;
  }
};

// --- Actions ---
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const createNewConversation = async () => {
  // If we are already in an empty new convo, don't create another
  if (currentConversation.value && messages.value.length === 0) return;

  try {
    const newConv = await chatService.createConversation({
      title: 'New Chat',
      model: selectedModel.value
    });
    conversations.value.unshift(newConv);
    selectConversation(newConv);
  } catch (error) {
    ElMessage.error('Failed to create chat');
  }
};

const selectConversation = async (conv) => {
  currentConversation.value = conv;
  selectedModel.value = conv.model; // Sync model
  try {
    messages.value = await chatService.getConversationMessages(conv.id);
  } catch (e) {
    ElMessage.error('Failed to load messages');
  }
};

const handleModelChange = (modelId) => {
  selectedModel.value = modelId;
  // If current conversation is empty, update its model? Or just for new messages?
  // Typically model is per-conversation in backend. 
  // For now, we update local state, next message sends this model.
};

const fillInput = (text) => {
  userInput.value = text;
};

const sendMessage = async () => {
  const text = userInput.value.trim();
  if (!text || isGenerating.value) return;

  // Auto-create conversation if missing
  if (!currentConversation.value) {
    try {
      await createNewConversation();
      // Double check if creation was successful
      if (!currentConversation.value) {
        ElMessage.error('Please create a new conversation first.');
        return;
      }
    } catch (e) {
      ElMessage.error('Failed to start a new conversation.');
      return;
    }
  }

  // Add user message
  const userMsg = { role: 'user', content: text };
  messages.value.push(userMsg);

  // Prepare assistant message placeholder
  const assistantMsg = { role: 'assistant', content: '', loading: true };
  messages.value.push(assistantMsg);

  userInput.value = '';
  isGenerating.value = true;
  scrollToBottom();

  try {
    await chatService.sendMessage({
      conversation_id: currentConversation.value.id,
      model: selectedModel.value,
      messages: messages.value.filter(m => !m.loading),
      stream: true,
      ...modelSettings.value
    }, (chunk, fullText) => {
      assistantMsg.content = fullText;
      scrollToBottom(); // Auto scroll during stream
    });

    assistantMsg.loading = false;

    // Update title if it's the first message
    const currentConv = conversations.value.find(c => c.id === currentConversation.value.id);
    if (currentConv && (currentConv.title === 'New Chat' || !currentConv.title)) {
      const newTitle = text.slice(0, 30);
      currentConv.title = newTitle;
      // Only update title if we have a valid ID
      if (currentConv.id) {
        await chatService.updateConversation(currentConv.id, { title: newTitle });
      }
    }
    // Update timestamp locally
    if (currentConv) currentConv.updated_at = new Date().toISOString();

  } catch (error) {
    assistantMsg.content = 'Error generating response: ' + (error.message || 'Unknown error');
    assistantMsg.error = true;
    assistantMsg.loading = false;
    console.error(error);
  } finally {
    isGenerating.value = false;
  }
};

const handleConvAction = (command, conv) => {
  if (command === 'rename') {
    conversationToRename.value = conv;
    newConversationTitle.value = conv.title;
    showRenameDialog.value = true;
  } else if (command === 'delete') {
    deleteConversation(conv);
  }
};

const renameConversation = async () => {
  if (!newConversationTitle.value.trim()) return;
  try {
    await chatService.updateConversation(conversationToRename.value.id, { title: newConversationTitle.value });
    conversationToRename.value.title = newConversationTitle.value;
    showRenameDialog.value = false;
  } catch (e) {
    ElMessage.error('Rename failed');
  }
};

const deleteConversation = async (conv) => {
  try {
    await ElMessageBox.confirm('Delete this conversation?', 'Warning', { type: 'warning' });
    await chatService.deleteConversation(conv.id);
    conversations.value = conversations.value.filter(c => c.id !== conv.id);
    if (currentConversation.value?.id === conv.id) {
      conversations.value.length > 0 ? selectConversation(conversations.value[0]) : createNewConversation();
    }
  } catch (e) {
    // cancelled
  }
};

const saveSettings = async () => {
  try {
    await chatService.updateModelSettings({ model: selectedModel.value, settings: modelSettings.value });
    showSettings.value = false;
    ElMessage.success('Settings saved');
  } catch (e) {
    ElMessage.error('Failed to save settings');
  }
};

const renderMarkdown = (text) => {
  return text ? marked(text) : '';
};

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('Copied to clipboard');
  } catch (err) {
    ElMessage.error('Failed to copy');
  }
};

</script>

<style scoped>
/* Reset & Base */
.gemini-layout {
  display: flex;
  height: 100vh;
  background-color: #f0f4f9;
  /* Light greyish blue like Gemini/Google */
  color: #1f1f1f;
  font-family: 'Google Sans', 'Roboto', sans-serif;
  /* Fallback */
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: #f0f4f9;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  padding: 12px;
  border-right: none;
  /* Gemini usually usually clean, maybe no border */
}

.sidebar-collapsed {
  width: 72px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.new-chat-btn {
  border-radius: 20px;
  background-color: #dde3ea;
  border: none;
  color: #444746;
  padding: 10px 16px;
  font-weight: 500;
  transition: all 0.2s;
  flex-grow: 1;
  justify-content: flex-start;
  margin-right: 8px;
}

.new-chat-btn:hover {
  background-color: #d3dbe5;
  color: #1f1f1f;
}

.new-chat-btn .icon {
  margin-right: 8px;
}

.collapse-btn {
  color: #444746;
}

.sidebar-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 12px;
  font-weight: 500;
  color: #444746;
  margin-bottom: 8px;
  padding-left: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 20px;
  cursor: pointer;
  color: #1f1f1f;
  transition: background-color 0.2s;
  margin-bottom: 4px;
}

.history-item:hover,
.history-item.active {
  background-color: #dde3ea;
}

.history-item.active {
  font-weight: 500;
}

.item-icon {
  margin-right: 12px;
  font-size: 16px;
  color: #444746;
}

.item-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.item-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .item-actions {
  opacity: 1;
  /* Show on hover */
}

.collapsed-actions {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.collapsed-new-btn {
  background-color: #dde3ea;
  border: none;
  color: #444746;
}

.sidebar-footer {
  padding-top: 10px;
}

/* Main Content */
.main-content {
  flex: 1;
  background-color: #fff;
  /* White card-like area */
  border-radius: 16px;
  margin: 12px 12px 12px 0;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.02);
  overflow: hidden;
}

.top-bar {
  padding: 16px 24px;
  display: flex;
  align-items: center;
}

.model-trigger {
  font-size: 18px;
  font-weight: 500;
  color: #444746;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.model-trigger:hover {
  background-color: #f0f4f9;
  border-radius: 8px;
  padding: 4px 8px;
  margin: -4px -8px;
}

/* Chat Area */
.chat-scroll-area {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
  padding: 0 20%;
  /* Center the chat */
}

@media (max-width: 1200px) {
  .chat-scroll-area {
    padding: 0 10%;
  }
}

@media (max-width: 768px) {
  .chat-scroll-area {
    padding: 0 16px;
  }

  .sidebar {
    position: absolute;
    z-index: 100;
    height: 100%;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }

  .sidebar-collapsed {
    width: 0;
    padding: 0;
  }

  .main-content {
    margin: 0;
    border-radius: 0;
  }
}


.chat-wrapper {
  padding: 40px 0 100px 0;
  /* Space for input */
}

/* Welcome Screen */
.welcome-screen {
  margin-top: 10vh;
  text-align: center;
  /* Center horizontally but content left aligned looks weird? Gemini is left aligned usually or center */
  display: flex;
  flex-direction: column;
  align-items: center;
}

.greeting h1 {
  font-size: 56px;
  font-weight: 500;
  background: linear-gradient(74deg, #4285f4 0, #9b72cb 9%, #d96570 20%, #d96570 24%, #9b72cb 35%, #4285f4 44%, #9b72cb 50%, #d96570 56%, #1f1f1f 75%, #1f1f1f 100%);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  /* Use generic color if gradient fails */
  color: #c4768d;
  /* Fallbackish */
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.greeting p {
  font-size: 24px;
  color: #c4c7c5;
  /* Muted */
  color: #8e8e8e;
}

.suggestion-chips {
  display: flex;
  gap: 12px;
  margin-top: 48px;
  flex-wrap: wrap;
  justify-content: center;
}

.chip {
  background-color: #f0f4f9;
  padding: 12px 18px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #1f1f1f;
  transition: background 0.2s;
}

.chip:hover {
  background-color: #dde3ea;
}

/* Messages */
.message-row {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  margin-top: 4px;
}

.message-avatar .user {
  background-color: #ab47bc;
}

/* Purple for user */
.message-avatar .assistant {
  background-color: #1976d2;
}

/* Blue for bot */

.message-content-wrapper {
  flex: 1;
  max-width: 100%;
}

.message-sender {
  font-weight: 500;
  margin-bottom: 4px;
  font-size: 14px;
  color: #444746;
}

.message-bubble {
  line-height: 1.6;
  font-size: 16px;
  color: #1f1f1f;
}

.message-bubble.error {
  color: #d32f2f;
}

.message-actions {
  margin-top: 8px;
  display: flex;
  gap: 12px;
}

.action-icon {
  cursor: pointer;
  font-size: 16px;
  color: #8e8e8e;
  transition: color 0.2s;
}

.action-icon:hover {
  color: #1f1f1f;
}

/* Input Area */
.input-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px 20%;
  background: linear-gradient(to top, #fff 80%, rgba(255, 255, 255, 0));
  z-index: 10;
}

@media (max-width: 1200px) {
  .input-container {
    padding: 24px 10%;
  }
}

@media (max-width: 768px) {
  .input-container {
    padding: 16px;
  }
}

.input-box {
  background-color: #f0f4f9;
  border-radius: 28px;
  padding: 8px 16px;
  display: flex;
  align-items: flex-end;
  /* Align button to bottom if multiline */
  transition: background-color 0.2s;
}

.input-box:focus-within {
  background-color: #dde3ea;
}

.chat-input :deep(.el-textarea__inner) {
  background-color: transparent;
  border: none;
  box-shadow: none;
  resize: none;
  padding: 12px 0;
  font-size: 16px;
  line-height: 1.5;
  color: #1f1f1f;
}

.input-actions {
  margin-bottom: 6px;
  margin-left: 8px;
}

.disclaimer {
  text-align: center;
  font-size: 11px;
  color: #8e8e8e;
  margin-top: 12px;
}

/* Typing Indicator */
.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: #444746;
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {

  0%,
  80%,
  100% {
    transform: scale(0);
  }

  40% {
    transform: scale(1);
  }
}

/* Markdown overrides */
:deep(.markdown-body) {
  background-color: transparent !important;
  font-family: inherit;
  font-size: 16px;
}

:deep(pre) {
  background-color: #f6f8fa;
  border-radius: 8px;
  padding: 16px;
  overflow: auto;
  margin: 12px 0;
}

:deep(code) {
  font-family: 'Roboto Mono', monospace;
  font-size: 14px;
}
</style>