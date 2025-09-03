import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import EnvInfo from '../EnvInfo.vue'

// 模拟Element Plus组件
vi.mock('@element-plus/icons-vue', () => ({
  InfoFilled: {}
}))

describe('EnvInfo.vue', () => {
  // 测试不同环境下的组件渲染
  describe('环境标签显示', () => {
    it('开发环境下显示绿色标签', () => {
      // 模拟开发环境
      vi.stubGlobal('import.meta', {
        env: {
          VITE_APP_ENV: 'dev',
          VITE_APP_API_URL: 'http://localhost:8001',
          VITE_APP_TITLE: 'LLM Trainer Dev',
          VITE_APP_DEBUG: 'true'
        }
      })

      const wrapper = mount(EnvInfo, {
        global: {
          stubs: ['el-tag', 'el-tooltip', 'el-button', 'el-icon', 'el-dialog', 'el-descriptions', 'el-descriptions-item']
        }
      })

      // 验证标签文本和类型
      expect(wrapper.find('.env-info').exists()).toBe(true)
      expect(wrapper.text()).toContain('开发环境')
      expect(wrapper.findComponent({ name: 'el-tag' }).attributes('type')).toBe('success')
    })

    it('测试环境下显示黄色标签', () => {
      // 模拟测试环境
      vi.stubGlobal('import.meta', {
        env: {
          VITE_APP_ENV: 'test',
          VITE_APP_API_URL: 'http://localhost:8001',
          VITE_APP_TITLE: 'LLM Trainer Test',
          VITE_APP_DEBUG: 'false'
        }
      })

      const wrapper = mount(EnvInfo, {
        global: {
          stubs: ['el-tag', 'el-tooltip', 'el-button', 'el-icon', 'el-dialog', 'el-descriptions', 'el-descriptions-item']
        }
      })

      expect(wrapper.find('.env-info').exists()).toBe(true)
      expect(wrapper.text()).toContain('测试环境')
      expect(wrapper.findComponent({ name: 'el-tag' }).attributes('type')).toBe('warning')
    })

    it('生产环境下不显示标签（除非开启调试）', () => {
      // 模拟生产环境
      vi.stubGlobal('import.meta', {
        env: {
          VITE_APP_ENV: 'prod',
          VITE_APP_API_URL: 'https://api.example.com',
          VITE_APP_TITLE: 'LLM Trainer',
          VITE_APP_DEBUG: 'false'
        }
      })

      const wrapper = mount(EnvInfo, {
        global: {
          stubs: ['el-tag', 'el-tooltip', 'el-button', 'el-icon', 'el-dialog', 'el-descriptions', 'el-descriptions-item']
        }
      })

      // 生产环境且调试关闭时不显示
      expect(wrapper.find('.env-info').exists()).toBe(false)
    })
  })

  // 测试环境详情对话框
  describe('环境详情对话框', () => {
    beforeEach(() => {
      // 每个测试前重置模拟
      vi.stubGlobal('import.meta', {
        env: {
          VITE_APP_ENV: 'dev',
          VITE_APP_API_URL: 'http://localhost:8001',
          VITE_APP_TITLE: 'LLM Trainer Dev',
          VITE_APP_DEBUG: 'true'
        }
      })
    })

    it('点击信息按钮打开对话框', async () => {
      const wrapper = mount(EnvInfo, {
        global: {
          stubs: ['el-tag', 'el-tooltip', 'el-button', 'el-icon', 'el-dialog', 'el-descriptions', 'el-descriptions-item']
        }
      })

      // 初始状态下对话框不可见
      expect(wrapper.vm.showEnvDetails).toBe(false)

      // 点击信息按钮
      await wrapper.find('el-button-stub').trigger('click')

      // 对话框应该可见
      expect(wrapper.vm.showEnvDetails).toBe(true)
    })
  })
})