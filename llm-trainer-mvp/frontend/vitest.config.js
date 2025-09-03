import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      // 设置覆盖率阈值
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
      // 排除不需要测试的文件
      exclude: [
        'node_modules/**',
        'dist/**',
        '**/*.d.ts',
        'src/main.js',
        'src/router.js',
        'src/assets/**'
      ]
    },
    // 设置别名，与vite.config.js保持一致
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    // 包含的文件模式
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx,vue}']
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})