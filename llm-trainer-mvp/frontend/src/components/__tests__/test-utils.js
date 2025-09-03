import { mount, shallowMount } from '@vue/test-utils'

/**
 * 创建通用的Element Plus组件存根
 * @returns {Object} Element Plus组件存根对象
 */
export function createElementPlusStubs() {
  return {
    'el-button': true,
    'el-input': true,
    'el-select': true,
    'el-option': true,
    'el-form': true,
    'el-form-item': true,
    'el-table': true,
    'el-table-column': true,
    'el-tag': true,
    'el-dialog': true,
    'el-card': true,
    'el-menu': true,
    'el-menu-item': true,
    'el-submenu': true,
    'el-dropdown': true,
    'el-dropdown-menu': true,
    'el-dropdown-item': true,
    'el-icon': true,
    'el-tooltip': true,
    'el-pagination': true,
    'el-alert': true,
    'el-descriptions': true,
    'el-descriptions-item': true,
  }
}

/**
 * 创建Vue Router模拟
 * @returns {Object} Vue Router模拟对象
 */
export function createRouterMock() {
  return {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    currentRoute: {
      value: {
        path: '/',
        params: {},
        query: {},
        hash: '',
        fullPath: '/',
        matched: [],
        meta: {},
        name: undefined
      }
    }
  }
}

/**
 * 挂载组件并提供通用模拟
 * @param {Component} component - Vue组件
 * @param {Object} options - 挂载选项
 * @returns {VueWrapper} 组件包装器
 */
export function mountWithGlobals(component, options = {}) {
  const { shallow = false, router = createRouterMock(), ...rest } = options
  
  const globalOptions = {
    stubs: createElementPlusStubs(),
    mocks: {
      $router: router
    },
    ...rest.global
  }
  
  const mountOptions = {
    ...rest,
    global: globalOptions
  }
  
  return shallow ? shallowMount(component, mountOptions) : mount(component, mountOptions)
}