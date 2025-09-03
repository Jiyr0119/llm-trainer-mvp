<template>
  <div class="env-info" v-if="showEnvInfo">
    <el-tag :type="envTagType" size="small">
      {{ envName }}
    </el-tag>
    <el-tooltip content="当前环境配置信息" placement="bottom" v-if="isDev">
      <el-button type="text" @click="showEnvDetails = true">
        <el-icon><InfoFilled /></el-icon>
      </el-button>
    </el-tooltip>
    
    <el-dialog
      v-model="showEnvDetails"
      title="环境配置信息"
      width="500px"
    >
      <div class="env-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="环境">{{ envName }}</el-descriptions-item>
          <el-descriptions-item label="API地址">{{ apiUrl }}</el-descriptions-item>
          <el-descriptions-item label="应用标题">{{ appTitle }}</el-descriptions-item>
          <el-descriptions-item label="调试模式">{{ isDebug ? '开启' : '关闭' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

// 环境变量
const env = import.meta.env.VITE_APP_ENV || 'dev'
const apiUrl = import.meta.env.VITE_APP_API_URL || 'http://localhost:8001'
const appTitle = import.meta.env.VITE_APP_TITLE || 'LLM Trainer'
const isDebug = import.meta.env.VITE_APP_DEBUG === 'true' || false

// 显示控制
const showEnvDetails = ref(false)
const showEnvInfo = computed(() => env !== 'prod' || isDebug)

// 计算属性
const isDev = computed(() => env === 'dev')
const envName = computed(() => {
  switch (env) {
    case 'dev': return '开发环境'
    case 'test': return '测试环境'
    case 'prod': return '生产环境'
    default: return `${env}环境`
  }
})

const envTagType = computed(() => {
  switch (env) {
    case 'dev': return 'success'
    case 'test': return 'warning'
    case 'prod': return 'danger'
    default: return 'info'
  }
})
</script>

<style scoped>
.env-info {
  display: inline-flex;
  align-items: center;
  margin-left: 10px;
}

.env-details {
  max-height: 400px;
  overflow-y: auto;
}
</style>