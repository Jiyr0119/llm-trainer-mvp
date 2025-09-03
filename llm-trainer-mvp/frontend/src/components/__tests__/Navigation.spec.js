import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Navigation from '../Navigation.vue'
import EnvInfo from '../EnvInfo.vue'
import { createElementPlusStubs, createRouterMock, mountWithGlobals } from './test-utils'

describe('Navigation组件', () => {
  // 创建路由模拟
  const router = createRouterMock({
    routes: [
      { path: '/', name: 'home' },
      { path: '/upload', name: 'upload' },
      { path: '/datasets', name: 'datasets' },
      { path: '/train', name: 'train' },
      { path: '/predict', name: 'predict' }
    ]
  })

  // 创建Element Plus组件存根
  const stubs = createElementPlusStubs(['ElMenu', 'ElMenuItem'])

  it('正确渲染所有导航菜单项', () => {
    const wrapper = mountWithGlobals(Navigation, {
      global: {
        plugins: [router],
        stubs: {
          ...stubs,
          EnvInfo: true // 存根EnvInfo组件
        }
      }
    })

    // 验证所有菜单项都存在
    const menuItems = wrapper.findAll('.el-menu-item')
    expect(menuItems.length).toBe(5)

    // 验证菜单项文本
    const menuTexts = menuItems.map(item => item.text())
    expect(menuTexts).toContain('首页')
    expect(menuTexts).toContain('数据上传')
    expect(menuTexts).toContain('数据集管理')
    expect(menuTexts).toContain('模型训练')
    expect(menuTexts).toContain('模型推理')
  })

  it('包含EnvInfo组件', () => {
    const wrapper = mountWithGlobals(Navigation, {
      global: {
        plugins: [router],
        stubs
      },
      shallow: false
    })

    // 验证EnvInfo组件存在
    expect(wrapper.findComponent(EnvInfo).exists()).toBe(true)
  })

  it('根据当前路由设置活动菜单项', async () => {
    // 模拟路由路径
    router.currentRoute.value.path = '/datasets'

    const wrapper = mountWithGlobals(Navigation, {
      global: {
        plugins: [router],
        stubs: {
          ...stubs,
          EnvInfo: true
        }
      }
    })

    // 验证ElMenu组件的default-active属性设置为当前路由路径
    const menu = wrapper.findComponent({ name: 'ElMenu' })
    expect(menu.attributes('default-active')).toBe('/datasets')

    // 改变路由并验证
    await router.push('/train')
    expect(wrapper.vm.$route.path).toBe('/train')
  })
})