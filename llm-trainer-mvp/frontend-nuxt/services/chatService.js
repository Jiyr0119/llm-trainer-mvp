import axios from './axios';
import { API_URL } from '../config';

const chatService = {
    /**
     * 获取可用的语言模型列表
     * @returns {Promise<Array>} 模型列表
     */
    async getModels() {
        try {
            const response = await axios.get(`${API_URL}/chat/models`);
            console.log('[ChatService] Get models response:', response.data);
            return response.data.models || [];
        } catch (error) {
            console.error('[ChatService] Get models failed:', error);
            throw error;
        }
    },

    /**
     * 获取对话列表
     * @returns {Promise<Array>} 对话列表
     */
    async getConversations() {
        try {
            const response = await axios.get(`${API_URL}/chat/conversations`);
            console.log('[ChatService] Get conversations response:', response.data);
            return response.data.conversations || [];
        } catch (error) {
            console.error('[ChatService] Get conversations failed:', error);
            throw error;
        }
    },

    /**
     * 创建新对话
     * @param {Object} data 对话数据
     * @returns {Promise<Object>} 创建的对话
     */
    async createConversation(data) {
        try {
            console.log('[ChatService] Creating conversation:', data);
            const response = await axios.post(`${API_URL}/chat/conversations`, data);
            console.log('[ChatService] Create conversation response:', response.data);
            return response.data;
        } catch (error) {
            console.error('[ChatService] Create conversation failed:', error);
            throw error;
        }
    },

    /**
     * 获取对话消息历史
     * @param {string} conversationId 对话ID
     * @returns {Promise<Array>} 消息列表
     */
    async getConversationMessages(conversationId) {
        try {
            console.log('[ChatService] Getting messages for conversation:', conversationId);
            const response = await axios.get(`${API_URL}/chat/conversations/${conversationId}`);
            console.log('[ChatService] Get messages response:', response.data);
            return response.data.messages || [];
        } catch (error) {
            console.error('[ChatService] Get messages failed:', error);
            throw error;
        }
    },

    /**
     * 更新对话信息
     * @param {string} conversationId 对话ID
     * @param {Object} data 更新数据
     * @returns {Promise<Object>} 更新后的对话
     */
    async updateConversation(conversationId, data) {
        try {
            console.log('[ChatService] Updating conversation:', conversationId, data);
            const response = await axios.patch(`${API_URL}/chat/conversations/${conversationId}`, data);
            console.log('[ChatService] Update conversation response:', response.data);
            return response.data;
        } catch (error) {
            console.error('[ChatService] Update conversation failed:', error);
            throw error;
        }
    },

    /**
     * 删除对话
     * @param {string} conversationId 对话ID
     * @returns {Promise<void>}
     */
    async deleteConversation(conversationId) {
        try {
            console.log('[ChatService] Deleting conversation:', conversationId);
            await axios.delete(`${API_URL}/chat/conversations/${conversationId}`);
            console.log('[ChatService] Delete conversation success');
        } catch (error) {
            console.error('[ChatService] Delete conversation failed:', error);
            throw error;
        }
    },

    /**
     * 发送消息并获取流式回复
     * @param {Object} data 消息数据
     * @param {Function} onStream 流式输出回调函数
     * @returns {Promise<Object>} 模型回复
     */
    async sendMessage(data, onStream = null) {
        try {
            console.log('[ChatService] Sending message:', {
                model: data.model,
                messageCount: data.messages.length,
                stream: data.stream
            });

            if (!onStream || !data.stream) {
                throw new Error('Stream mode is required. Please provide onStream callback.');
            }

            const response = await fetch(`${API_URL}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({
                    model: data.model,
                    messages: data.messages.map(m => ({
                        role: m.role,
                        content: m.content
                    })),
                    temperature: data.temperature || 0.7,
                    max_tokens: data.max_tokens || 2048,
                    stream: true
                })
            });

            if (!response.ok) {
                let errorMessage = 'Failed to send message';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch (e) {
                    errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';
            let fullResponse = '';
            let hadError = false;

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        console.log('[ChatService] Stream completed');
                        break;
                    }

                    buffer += decoder.decode(value, { stream: true });

                    // SSE协议: 使用双换行符分隔事件
                    const events = buffer.split('\n\n');
                    buffer = events.pop() || ''; // 保留未完成的部分

                    for (const event of events) {
                        const lines = event.split('\n');
                        for (const line of lines) {
                            if (!line.trim()) continue;

                            if (line.startsWith('data: ')) {
                                const dataStr = line.slice(6).trim();
                                if (dataStr === '[DONE]') {
                                    console.log('[ChatService] Received [DONE]');
                                    continue;
                                }

                                try {
                                    const json = JSON.parse(dataStr);

                                    if (json.choices && json.choices.length > 0) {
                                        const delta = json.choices[0].delta;
                                        if (delta && delta.content) {
                                            fullResponse += delta.content;
                                            onStream(delta.content, fullResponse);
                                        }
                                    }
                                } catch (e) {
                                    console.warn('[ChatService] Failed to parse JSON:', dataStr, e);
                                }
                            }
                        }
                    }
                }

                return {
                    id: `chatcmpl-${Date.now()}`,
                    model: data.model,
                    choices: [{
                        message: {
                            role: 'assistant',
                            content: fullResponse
                        },
                        finish_reason: 'stop'
                    }],
                    created: Math.floor(Date.now() / 1000)
                };
            } catch (streamError) {
                console.error('[ChatService] Stream processing error:', streamError);
                throw streamError;
            }
        } catch (error) {
            console.error('[ChatService] Send message failed:', error);
            throw error;
        }
    },

    /**
     * 更新模型设置
     * @param {Object} data 设置数据
     * @returns {Promise<Object>} 更新后的设置
     */
    async updateModelSettings(data) {
        try {
            console.log('[ChatService] Updating model settings:', data);
            const response = await axios.patch(`${API_URL}/chat/models/settings`, data);
            console.log('[ChatService] Update settings response:', response.data);
            return response.data;
        } catch (error) {
            console.error('[ChatService] Update settings failed:', error);
            throw error;
        }
    }
};

export default chatService;
