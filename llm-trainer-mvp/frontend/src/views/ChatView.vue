<template>
  <div class="chat-container">
    <el-row :gutter="20">
      <!-- 左侧会话列表 -->
      <el-col :span="6">
        <div class="conversation-list">
          <div class="list-header">
            <h3>对话历史</h3>
            <el-button type="primary" size="small" @click="createNewConversation">
              <el-icon><Plus /></el-icon> 新对话
            </el-button>
          </div>
          
          <el-scrollbar height="calc(100vh - 180px)">
            <div 
              v-for="conv in conversations" 
              :key="conv.id"
              class="conversation-item"
              :class="{ active: currentConversation?.id === conv.id }"
              @click="selectConversation(conv)"
            >
              <div class="conv-title">{{ conv.title || '新对话' }}</div>
              <div class="conv-time">{{ formatDate(conv.updated_at) }}</div>
              <el-dropdown trigger="click" @command="handleConvAction($event, conv)">
                <el-icon><More /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="rename">重命名</el-dropdown-item>
                    <el-dropdown-item command="export">导出</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-scrollbar>
        </div>
      </el-col>
      
      <!-- 右侧对话区域 -->
      <el-col :span="18">
        <div class="chat-area">
          <!-- 模型选择和设置 -->
          <div class="model-settings">
            <el-select v-model="selectedModel" placeholder="选择模型" size="large">
              <el-option 
                v-for="model in availableModels" 
                :key="model.id" 
                :label="model.name" 
                :value="model.id"
              >
                <div class="model-option">
                  <span>{{ model.name }}</span>
                  <span class="model-description">{{ model.description }}</span>
                </div>
              </el-option>
            </el-select>
            
            <el-button @click="showSettings = true">
              <el-icon><Setting /></el-icon>
            </el-button>
          </div>
          
          <!-- 消息区域 -->
          <el-scrollbar ref="messageScrollbar" height="calc(100vh - 240px)" class="message-area">
            <div v-if="messages.length === 0" class="empty-state">
              <el-empty description="开始一个新的对话吧" />
            </div>
            <div v-else>
              <div 
                v-for="(message, index) in messages" 
                :key="index"
                class="message"
                :class="message.role"
              >
                <div class="message-avatar">
                  <el-avatar :icon="message.role === 'user' ? UserFilled : Monitor" />
                </div>
                <div class="message-content" :class="{ 'error-message': message.error }">
                  <div v-if="message.role === 'assistant' && message.loading" class="loading-dots">
                    <span></span><span></span><span></span>
                  </div>
                  <div v-else-if="message.content" v-html="renderMarkdown(message.content)"></div>
                  <div v-else class="empty-message">无内容</div>
                  <div v-if="message.role === 'assistant' && message.responseTime && !message.error" class="response-time">
                    响应时间: {{ message.responseTime.toFixed(2) }}秒
                  </div>
                </div>
              </div>
            </div>
          </el-scrollbar>
          
          <!-- 输入区域 -->
          <div class="input-area">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="3"
              placeholder="输入您的问题..."
              resize="none"
              @keydown.enter.exact.prevent="sendMessage"
            />
            <div class="input-actions">
              <span class="hint">按 Enter 发送，Shift+Enter 换行</span>
              <el-button type="primary" :disabled="!userInput.trim() || isGenerating" @click="sendMessage">
                发送
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="模型参数设置" width="500px">
      <el-form label-position="top">
        <el-form-item label="温度 (Temperature)">
          <el-slider
            v-model="modelSettings.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
          />
          <div class="setting-description">较高的值会使输出更加随机，较低的值会使其更加集中和确定性</div>
        </el-form-item>
        
        <el-form-item label="最大生成长度">
          <el-slider
            v-model="modelSettings.max_tokens"
            :min="10"
            :max="4096"
            :step="10"
            show-input
          />
          <div class="setting-description">控制生成文本的最大长度</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSettings = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重命名对话框 -->
    <el-dialog v-model="showRenameDialog" title="重命名对话" width="400px">
      <el-input v-model="newConversationTitle" placeholder="输入对话名称" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRenameDialog = false">取消</el-button>
          <el-button type="primary" @click="renameConversation">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import { Plus, More, Setting, UserFilled, Monitor } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import chatService from '../services/chatService';

// 初始化marked配置
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true
});

// 状态变量
const conversations = ref([]);
const currentConversation = ref(null);
const messages = ref([]);
const userInput = ref('');
const isGenerating = ref(false);
const messageScrollbar = ref(null);
const typingSpeed = ref(20); // 打字机效果的速度（毫秒/字符）

// 模型相关
const availableModels = ref([]);
const selectedModel = ref('');
const modelSettings = ref({
  temperature: 0.7,
  max_tokens: 1024
});

// 对话框控制
const showSettings = ref(false);
const showRenameDialog = ref(false);
const newConversationTitle = ref('');
const conversationToRename = ref(null);

// 初始化
onMounted(async () => {
  try {
    // 加载可用模型
    const models = await chatService.getModels();
    availableModels.value = models;
    if (models.length > 0) {
      selectedModel.value = models[0].id;
    }
    
    // 加载对话历史
    const convs = await chatService.getConversations();
    conversations.value = convs;
    
    // 如果有对话，选择最近的一个
    if (convs.length > 0) {
      selectConversation(convs[0]);
    } else {
      createNewConversation();
    }
  } catch (error) {
    ElMessage.error('初始化失败: ' + error.message);
  }
});

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    if (messageScrollbar.value) {
      messageScrollbar.value.setScrollTop(9999);
    }
  });
}, { deep: true });

// 方法
const createNewConversation = async () => {
  try {
    const newConv = await chatService.createConversation({
      title: '新对话',
      model: selectedModel.value
    });
    conversations.value.unshift(newConv);
    selectConversation(newConv);
  } catch (error) {
    ElMessage.error('创建对话失败: ' + error.message);
  }
};

const selectConversation = async (conversation) => {
  currentConversation.value = conversation;
  try {
    const messagesData = await chatService.getConversationMessages(conversation.id);
    messages.value = messagesData;
    selectedModel.value = conversation.model;
  } catch (error) {
    ElMessage.error('加载对话消息失败: ' + error.message);
    messages.value = [];
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isGenerating.value) return;
  
  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: userInput.value.trim()
  };
  messages.value.push(userMessage);
  
  // 添加助手消息（加载中状态）
  const assistantMessage = {
    role: 'assistant',
    content: '',
    loading: true,
    startTime: new Date() // 记录开始时间
  };
  messages.value.push(assistantMessage);
  
  // 清空输入框
  userInput.value = '';
  isGenerating.value = true;
  
  try {
    // 使用流式输出
    await chatService.sendMessage({
      conversation_id: currentConversation.value.id,
      model: selectedModel.value,
      messages: messages.value.filter(m => !m.loading),
      stream: true, // 确保启用流式输出
      ...modelSettings.value
    }, (chunk, fullText) => {
      // 实时更新助手消息内容
      assistantMessage.content = fullText;
    }).catch(error => {
      // 捕获并处理流式输出过程中的错误
      throw new Error(`生成回复时出错: ${error.message || '未知错误'}`); 
    });
    
    // 流式输出完成后
    assistantMessage.loading = false;
    assistantMessage.endTime = new Date(); // 记录结束时间
    assistantMessage.responseTime = (assistantMessage.endTime - assistantMessage.startTime) / 1000; // 计算响应时间（秒）
    
    // 更新对话列表
    const updatedConv = conversations.value.find(c => c.id === currentConversation.value.id);
    if (updatedConv) {
      updatedConv.updated_at = new Date().toISOString();
      if (!updatedConv.title || updatedConv.title === '新对话') {
        updatedConv.title = userMessage.content.substring(0, 30);
        await chatService.updateConversation(updatedConv.id, { title: updatedConv.title });
      }
    }
  } catch (error) {
    // 更友好的错误提示
    assistantMessage.content = `⚠️ 生成回复时出错: ${error.message || '未知错误'}`;
    assistantMessage.loading = false;
    assistantMessage.error = true;
    ElMessage({
      message: '发送消息失败: ' + error.message,
      type: 'error',
      duration: 5000,
      showClose: true
    });
  } finally {
    isGenerating.value = false;
  }
};

const handleConvAction = (command, conversation) => {
  switch (command) {
    case 'rename':
      conversationToRename.value = conversation;
      newConversationTitle.value = conversation.title;
      showRenameDialog.value = true;
      break;
    case 'export':
      exportConversation(conversation);
      break;
    case 'delete':
      deleteConversation(conversation);
      break;
  }
};

const renameConversation = async () => {
  if (!newConversationTitle.value.trim()) {
    ElMessage.warning('对话名称不能为空');
    return;
  }
  
  try {
    await chatService.updateConversation(conversationToRename.value.id, {
      title: newConversationTitle.value
    });
    
    const conv = conversations.value.find(c => c.id === conversationToRename.value.id);
    if (conv) {
      conv.title = newConversationTitle.value;
    }
    
    showRenameDialog.value = false;
    ElMessage.success('重命名成功');
  } catch (error) {
    ElMessage.error('重命名失败: ' + error.message);
  }
};

const deleteConversation = async (conversation) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await chatService.deleteConversation(conversation.id);
    conversations.value = conversations.value.filter(c => c.id !== conversation.id);
    
    if (currentConversation.value?.id === conversation.id) {
      if (conversations.value.length > 0) {
        selectConversation(conversations.value[0]);
      } else {
        currentConversation.value = null;
        messages.value = [];
        createNewConversation();
      }
    }
    
    ElMessage.success('删除成功');
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || error));
    }
  }
};

const exportConversation = (conversation) => {
  // 实现导出功能
  ElMessage.info('导出功能开发中...');
};

const saveSettings = async () => {
  try {
    await chatService.updateModelSettings({
      model: selectedModel.value,
      settings: modelSettings.value
    });
    showSettings.value = false;
    ElMessage.success('设置已保存');
  } catch (error) {
    ElMessage.error('保存设置失败: ' + error.message);
  }
};

const renderMarkdown = (text) => {
  if (!text) return '';
  return marked(text);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.chat-container {
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background-color: #f5f7fa;
}

.conversation-list {
  background-color: white;
  border-radius: 8px;
  height: calc(100vh - 40px);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.list-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
}

.conversation-item {
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.conversation-item:hover {
  background-color: #f5f7fa;
  transform: translateX(2px);
}

.conversation-item.active {
  background-color: #ecf5ff;
  border-left: 3px solid #4158D0;
}

.conversation-item:hover {
  background-color: #f5f7fa;
}

.conversation-item.active {
  background-color: #ecf5ff;
}

.conv-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 24px;
}

.conv-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.conversation-item .el-dropdown {
  position: absolute;
  right: 12px;
  top: 12px;
}

.chat-area {
  background-color: white;
  border-radius: 8px;
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.model-settings {
  padding: 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
}

.model-settings .el-select {
  flex: 1;
  margin-right: 12px;
}

.model-settings .el-select .el-input__wrapper {
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.model-settings .el-button {
  border-radius: 8px;
  padding: 8px 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.model-settings .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.model-option {
  display: flex;
  flex-direction: column;
}

.model-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.message-area {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: linear-gradient(to bottom, #ffffff, #f8f9fa);
}

.message-area::-webkit-scrollbar {
  width: 6px;
}

.message-area::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.message-area::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.message-area::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message {
  display: flex;
  margin-bottom: 24px;
}

.message-avatar {
  margin-right: 12px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: calc(100% - 60px);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}

.message.user .message-content {
  background: linear-gradient(135deg, #4158D0, #6C7FD8);
  color: white;
  border-bottom-right-radius: 0;
}

.message.assistant .message-content {
  background-color: #f5f7fa;
  border-bottom-left-radius: 0;
}

.error-message {
  background-color: #fef0f0 !important;
  border-left: 4px solid #f56c6c;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background-color: #f5f7fa;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-actions .el-button {
  padding: 8px 20px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.input-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.input-actions .el-button:active {
  transform: translateY(0);
}

.hint {
  font-size: 12px;
  color: #909399;
}

.setting-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 打字机效果和加载指示器 */
.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 24px;
}

.loading-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409eff;
  margin: 0 4px;
  animation: dot-flashing 1s infinite alternate;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-flashing {
  0% {
    opacity: 0.2;
  }
  100% {
    opacity: 1;
  }
}

/* 打字机效果 */
.typewriter-effect {
  display: inline-block;
  overflow: hidden;
  border-right: 2px solid #409eff;
  white-space: nowrap;
  margin: 0;
  animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
}

@keyframes typing {
  from { width: 0 }
  to { width: 100% }
}

@keyframes blink-caret {
  from, to { border-color: transparent }
  50% { border-color: #409eff }
}

.empty-message {
  color: #909399;
  font-style: italic;
}

.response-time {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  text-align: right;
  font-style: italic;
}

:deep(.markdown-body) {
  font-size: 14px;
}

:deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow: auto;
}

:deep(code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
}

:deep(p) {
  margin: 8px 0;
}
</style>