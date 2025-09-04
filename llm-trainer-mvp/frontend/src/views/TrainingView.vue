<template>
  <div class="training">
    <!-- 训练配置卡片 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型训练</span>
        </div>
      </template>
      <div class="content">
        <!-- 数据集选择和训练参数配置表单 -->
        <div class="dataset-selection">
          <el-form :model="trainingForm" label-width="120px">
            <!-- 数据集选择下拉框 -->
            <el-form-item label="选择数据集">
              <el-select v-model="trainingForm.dataset_id" placeholder="请选择数据集" style="width: 100%;">
                <el-option
                  v-for="dataset in datasets"
                  :key="dataset.id"
                  :label="dataset.name"
                  :value="dataset.id"
                />
              </el-select>
            </el-form-item>
            
            <!-- 训练轮数滑块，范围1-10 -->
            <el-form-item label="训练轮数">
              <el-slider v-model="trainingForm.epochs" :min="1" :max="10" show-input style="width: 100%;" />
            </el-form-item>
            
            <!-- 学习率输入框，支持精确调整 -->
            <el-form-item label="学习率">
              <el-input-number v-model="trainingForm.learning_rate" :min="1e-6" :max="1e-3" :step="1e-6" :precision="6" />
            </el-form-item>
            
            <!-- 批次大小选择 -->
            <el-form-item label="批次大小">
              <el-select v-model="trainingForm.batch_size" placeholder="请选择批次大小">
                <el-option label="4" :value="4" />
                <el-option label="8" :value="8" />
                <el-option label="16" :value="16" />
              </el-select>
            </el-form-item>
            
            <!-- 操作按钮：开始训练和停止训练 -->
            <el-form-item>
              <el-button type="primary" @click="startTraining" :loading="training">开始训练</el-button>
              <el-button type="danger" @click="stopTraining" :disabled="!currentJobId || trainingStatus !== 'running'">停止训练</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 训练状态显示区域，仅当有当前任务ID时显示 -->
        <div class="training-status" v-if="currentJobId">
          <!-- 状态提示信息 -->
          <el-alert
            :title="statusMessage"
            :type="statusType"
            show-icon
          />
          
          <!-- 训练进度条，仅在训练运行中时显示 -->
          <div class="progress-container" v-if="trainingStatus === 'running'">
            <h4>训练进度: {{ Math.round(trainingProgress) }}%</h4>
            <el-progress :percentage="trainingProgress" :status="progressStatus" />
          </div>
          
          <!-- 训练日志显示区域，仅当有日志时显示 -->
          <div class="logs-container" v-if="trainingLogs.length > 0">
            <h4>训练日志:</h4>
            <el-card class="log-card">
              <pre class="logs">{{ trainingLogs.join('') }}</pre>
            </el-card>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 训练任务列表卡片 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>训练任务列表</span>
          <el-button type="primary" size="small" @click="loadTrainingJobs">刷新</el-button>
        </div>
      </template>
      <div class="jobs-list">
        <!-- 训练任务表格 -->
        <el-table :data="trainingJobs || []" style="width: 100%">
          <el-table-column prop="id" label="任务ID" width="80" />
          <el-table-column prop="dataset_id" label="数据集ID" width="100" />
          <!-- 状态列，使用不同颜色的标签显示 -->
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <!-- 进度列，使用进度条显示 -->
          <el-table-column prop="progress" label="进度">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress || 0" :status="getProgressStatus(scope.row.status)" />
            </template>
          </el-table-column>
          <!-- 操作列 -->
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" text @click="viewJobDetails(scope.row.id)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- 可用数据集列表卡片 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>可用数据集</span>
        </div>
      </template>
      <div class="dataset-list">
        <!-- 可用数据集表格 -->
        <el-table :data="datasets || []" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="created_at" label="创建时间" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 导入API服务和Vue相关功能
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { datasetService, trainingService } from '../services/api'

// 获取路由实例
const route = useRoute()

// 响应式状态
const datasets = ref([]) // 可用数据集列表
// 训练表单数据
const trainingForm = reactive({
  dataset_id: '', // 选择的数据集ID
  epochs: 3, // 默认训练轮数
  learning_rate: 2e-5, // 默认学习率
  batch_size: 16 // 默认批次大小
})

const training = ref(false) // 训练状态标志
const statusMessage = ref('') // 状态消息
const statusType = ref('info') // 状态类型（用于控制提示框颜色）
const currentJobId = ref(null) // 当前训练任务ID
const trainingStatus = ref('') // 训练状态
const trainingProgress = ref(0) // 训练进度
const trainingLogs = ref([]) // 训练日志
let pollingInterval = null // 轮询间隔定时器
const trainingJobs = ref([]) // 训练任务列表

// 计算属性
const progressStatus = computed(() => {
  if (trainingStatus.value === 'succeeded' || trainingStatus.value === 'completed') return 'success' // 成功状态
  if (trainingStatus.value === 'failed') return 'exception' // 失败状态
  if (trainingStatus.value === 'stopped') return 'warning' // 停止状态
  return '' // 默认状态（进行中）
})

// 组件挂载后的生命周期钩子
onMounted(async () => {
  // 加载数据集和训练任务列表
  await loadDatasets()
  await loadTrainingJobs()
  
  // 检查URL参数中是否有datasetId，如果有则自动选择该数据集
  const datasetId = route.query.datasetId
  if (datasetId) {
    trainingForm.dataset_id = parseInt(datasetId, 10)
  }
})

// 组件卸载前的生命周期钩子
onBeforeUnmount(() => {
  // 组件销毁前清除轮询，防止内存泄漏
  clearPolling()
})

// 方法定义
async function loadDatasets() {
  try {
    // 直接使用datasetService.getDatasets()，不再需要适配器
    datasets.value = await datasetService.getDatasets()
  } catch (error) {
    console.error('Load datasets error:', error)
    ElMessage.error('加载数据集失败: ' + (error.message || '未知错误'))
    datasets.value = []
  }
}

async function loadTrainingJobs() {
  try {
    // 直接使用trainingService.getTrainingJobs()，不再需要适配器
    trainingJobs.value = await trainingService.getTrainingJobs()
  } catch (error) {
    console.error('Load training jobs error:', error)
    ElMessage.error('加载训练任务列表失败: ' + (error.message || '未知错误'))
    trainingJobs.value = []
  }
}
// 开始训练方法
async function startTraining() {
  // 表单验证：检查是否选择了数据集
  if (!trainingForm.dataset_id) {
    ElMessage.warning('请选择一个数据集')
    return
  }
  
  // 设置训练状态为进行中
  training.value = true
  statusMessage.value = '正在启动训练任务...'
  statusType.value = 'info'
  
  try {
    // 调用训练服务开始训练，传递训练参数
    const result = await trainingService.startTraining(trainingForm)
    
    // 保存返回的任务ID并初始化状态
    currentJobId.value = result.job_id
    trainingStatus.value = 'pending'
    trainingProgress.value = 0
    trainingLogs.value = []
    
    // 更新状态消息
    statusMessage.value = '训练任务已启动'
    statusType.value = 'success'
    
    // 启动轮询获取训练状态
    startPolling()
    
    // 重新加载训练任务列表以显示新任务
    await loadTrainingJobs()
  } catch (error) {
    // 处理训练启动失败的情况
    console.error('Start training error:', error)
    statusMessage.value = '训练任务启动失败: ' + (error.message || '未知错误')
    statusType.value = 'error'
    ElMessage.error(statusMessage.value)
  } finally {
    // 重置训练状态标志
    training.value = false
  }
}
// 停止训练方法
async function stopTraining() {
  // 检查是否有当前任务ID
  if (!currentJobId.value) {
    ElMessage.warning('没有正在运行的训练任务')
    return
  }
  
  try {
    // 调用训练服务停止训练，传递任务ID
    await trainingService.stopTraining(currentJobId.value)
    
    // 更新状态消息
    statusMessage.value = '已发送停止训练请求'
    statusType.value = 'info'
    ElMessage.success('停止训练请求已发送')
    
    // 停止轮询
    clearPolling()
  } catch (error) {
    // 处理停止训练失败的情况
    console.error('Stop training error:', error)
    ElMessage.error('停止训练失败: ' + (error.message || '未知错误'))
  }
}
// 获取训练状态方法
async function getTrainingStatus() {
  // 检查是否有当前任务ID
  if (!currentJobId.value) return
  
  try {
    // 调用训练服务获取训练状态，传递任务ID
    const status = await trainingService.getTrainingStatus(currentJobId.value)
    
    // 更新组件状态数据
    trainingStatus.value = status.status
    trainingProgress.value = status.progress || 0
    
    // 根据训练状态更新状态消息和类型
    switch (status.status) {
      case 'pending':
        statusMessage.value = '训练任务正在等待中...'
        statusType.value = 'info'
        break
      case 'running':
        statusMessage.value = '训练进行中...'
        statusType.value = 'info'
        break
      case 'succeeded':
      case 'completed':  // 添加对completed状态的支持
        statusMessage.value = '训练已完成'
        statusType.value = 'success'
        // 训练完成后停止轮询
        clearPolling()
        // 重新加载训练任务列表以更新状态
        setTimeout(() => {
          loadTrainingJobs()
        }, 1000) // 延迟1秒再加载，避免过于频繁的请求
        break
      case 'failed':
        statusMessage.value = '训练失败: ' + (status.error || '未知错误')
        statusType.value = 'error'
        // 训练失败后停止轮询
        clearPolling()
        // 延迟加载训练任务列表
        setTimeout(() => {
          loadTrainingJobs()
        }, 1000) // 延迟1秒再加载
        break
      case 'stopped':
        statusMessage.value = '训练已停止'
        statusType.value = 'warning'
        // 训练停止后停止轮询
        clearPolling()
        // 延迟加载训练任务列表
        setTimeout(() => {
          loadTrainingJobs()
        }, 1000) // 延迟1秒再加载
        break
    }
  } catch (error) {
    // 处理获取训练状态失败的情况
    console.error('Get training status error:', error)
    statusMessage.value = '获取训练状态失败: ' + (error.message || '未知错误')
    statusType.value = 'error'
  }
}
// 获取训练日志方法
async function getTrainingLogs() {
  // 检查是否有当前任务ID
  if (!currentJobId.value) return
  
  try {
    // 调用训练服务获取训练日志，传递任务ID和行数参数
    const logs = await trainingService.getTrainingLogs(currentJobId.value, 50)
    // 更新组件日志数据
    trainingLogs.value = logs || []
  } catch (error) {
    // 处理获取训练日志失败的情况
    console.error('Get training logs error:', error)
    ElMessage.error('获取训练日志失败: ' + (error.message || '未知错误'))
  }
}
// 启动轮询方法
function startPolling() {
  // 先清除现有的轮询定时器（如果有）
  clearPolling()
  
  // 设置新的轮询定时器，每2秒获取一次训练状态和日志
  pollingInterval = setInterval(async () => {
    await getTrainingStatus()
    await getTrainingLogs()
  }, 2000)
}
// 清除轮询方法
function clearPolling() {
  // 检查并清除轮询定时器
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}
// 查看任务详情方法
async function viewJobDetails(jobId) {
  try {
    // 获取指定任务的详细状态
    const status = await trainingService.getTrainingStatus(jobId)
    
    // 构造详细信息消息
    const details = `
任务ID: ${status.job_id}
状态: ${status.status}
进度: ${status.progress || 0}%
当前轮数: ${status.current_epoch || 0}/${status.total_epochs || 0}
损失值: ${status.loss !== null ? status.loss.toFixed(4) : 'N/A'}
准确率: ${status.accuracy !== null ? (status.accuracy * 100).toFixed(2) + '%' : 'N/A'}
创建时间: ${status.created_at || 'N/A'}
更新时间: ${status.updated_at || 'N/A'}
    `.trim()
    
    // 显示详细信息对话框
    ElMessageBox.alert(details, '任务详情', {
      confirmButtonText: '确定',
      customClass: 'job-details-dialog'
    })
  } catch (error) {
    // 处理获取任务详情失败的情况
    console.error('View job details error:', error)
    ElMessage.error('获取任务详情失败: ' + (error.message || '未知错误'))
  }
}
// 根据任务状态返回对应标签类型的方法
function getStatusType(status) {
  const statusTypes = {
    pending: 'info',
    running: 'primary',
    succeeded: 'success',
    completed: 'success',  // 添加对completed状态的支持
    failed: 'danger',
    stopped: 'warning'
  }
  return statusTypes[status] || 'info'
}

// 根据任务状态返回对应进度条状态的方法
function getProgressStatus(status) {
  const progressStatuses = {
    succeeded: 'success',
    completed: 'success',  // 添加对completed状态的支持
    failed: 'exception',
    stopped: 'warning'
  }
  return progressStatuses[status] || ''
}
</script>

<style scoped>
.training {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.training-status {
  margin-top: 20px;
}

.progress-container {
  margin-top: 20px;
}

.logs-container {
  margin-top: 20px;
}

.log-card {
  max-height: 300px;
  overflow-y: auto;
}

.logs {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.4;
}
</style>