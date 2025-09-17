import axios from 'axios';
import { API_URL } from '../config';

const chatService = {
  /**
   * 获取可用的语言模型列表
   * @returns {Promise<Array>} 模型列表
   */
  async getModels() {
    try {
      const response = await axios.get(`${API_URL}/chat/models`);
      return response.data.models || [];
    } catch (error) {
      console.error('获取模型列表失败:', error);
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
      return response.data.conversations || [];
    } catch (error) {
      console.error('获取对话列表失败:', error);
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
      const response = await axios.post(`${API_URL}/chat/conversations`, data);
      return response.data;
    } catch (error) {
      console.error('创建对话失败:', error);
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
      const response = await axios.get(`${API_URL}/chat/conversations/${conversationId}`);
      return response.data.messages || [];
    } catch (error) {
      console.error('获取对话消息失败:', error);
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
      const response = await axios.patch(`${API_URL}/chat/conversations/${conversationId}`, data);
      return response.data;
    } catch (error) {
      console.error('更新对话失败:', error);
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
      await axios.delete(`${API_URL}/chat/conversations/${conversationId}`);
    } catch (error) {
      console.error('删除对话失败:', error);
      throw error;
    }
  },

  /**
   * 发送消息并获取回复
   * @param {Object} data 消息数据
   * @param {Function} onStream 流式输出回调函数
   * @returns {Promise<Object>} 模型回复
   */
  async sendMessage(data, onStream = null) {
    try {
      // 如果提供了流式输出回调，使用流式输出
      if (onStream) {
        const response = await fetch(`${API_URL}/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            model: data.model,
            messages: data.messages.map(m => ({
              role: m.role,
              content: m.content
            })),
            temperature: data.temperature,
            max_tokens: data.max_tokens,
            stream: true
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '发送消息失败');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let fullResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') continue;
              
              try {
                const json = JSON.parse(data);
                if (json.choices && json.choices[0].delta) {
                  const delta = json.choices[0].delta;
                  if (delta.content) {
                    fullResponse += delta.content;
                    onStream(delta.content, fullResponse);
                  }
                }
              } catch (e) {
                console.error('解析流式输出失败:', e);
              }
            }
          }
        }

        return {
          id: `chatcmpl-${Date.now()}`,
          model: data.model,
          choices: [
            {
              message: {
                role: 'assistant',
                content: fullResponse
              },
              finish_reason: 'stop'
            }
          ],
          created: Math.floor(Date.now() / 1000)
        };
      } else {
        // 非流式输出
        const response = await axios.post(`${API_URL}/chat/completions`, {
          model: data.model,
          messages: data.messages.map(m => ({
            role: m.role,
            content: m.content
          })),
          temperature: data.temperature,
          max_tokens: data.max_tokens,
          stream: false
        });
        return response.data;
      }
    } catch (error) {
      console.error('发送消息失败:', error);
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
      const response = await axios.patch(`${API_URL}/chat/models/settings`, {
        model: data.model,
        settings: data.settings
      });
      return response.data;
    } catch (error) {
      console.error('更新模型设置失败:', error);
      throw error;
    }
  }
};

export default chatService;