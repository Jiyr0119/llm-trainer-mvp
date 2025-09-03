import { afterEach } from 'vitest'
import { cleanup } from '@vue/test-utils'

// 每个测试后自动清理
afterEach(() => {
  cleanup()
})