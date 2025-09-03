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
              <el-button size="small" @click="viewJobDetails(scope.row.id)">查看详情</el-button>
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

<script>
// 导入API服务
import { datasetService, trainingService } from '../services/api'

export default {
  name: 'TrainingView', // 组件名称
  data() {
    return {
      datasets: [], // 可用数据集列表
      // 训练表单数据
      trainingForm: {
        dataset_id: '', // 选择的数据集ID
        epochs: 3, // 默认训练轮数
        learning_rate: 2e-5, // 默认学习率
        batch_size: 16 // 默认批次大小
      },
      training: false, // 训练状态标志
      statusMessage: '', // 状态消息
      statusType: 'info', // 状态类型（用于控制提示框颜色）
      currentJobId: null, // 当前训练任务ID
      trainingStatus: '', // 训练状态
      trainingProgress: 0, // 训练进度
      trainingLogs: [], // 训练日志
      pollingInterval: null, // 轮询间隔定时器
      trainingJobs: [] // 训练任务列表
    }
  },
  // 计算属性
  computed: {
    // 根据训练状态返回进度条的状态类型
    progressStatus() {
      if (this.trainingStatus === 'succeeded') return 'success' // 成功状态
      if (this.trainingStatus === 'failed') return 'exception' // 失败状态
      if (this.trainingStatus === 'stopped') return 'warning' // 停止状态
      return '' // 默认状态（进行中）
    }
  },
  // 组件挂载后的生命周期钩子
  async mounted() {
    // 加载数据集和训练任务列表
    await this.loadDatasets()
    await this.loadTrainingJobs()
    
    // 检查URL参数中是否有datasetId，如果有则自动选择该数据集
    const datasetId = this.$route.query.datasetId
    if (datasetId) {
      this.trainingForm.dataset_id = parseInt(datasetId, 10)
    }
  },
  // 组件卸载前的生命周期钩子
  beforeUnmount() {
    // 组件销毁前清除轮询，防止内存泄漏
    this.clearPolling()
  },
  methods: {
    async loadDatasets() {
      try {
        const response = await datasetService.getDatasets()
        // 确保datasets是一个数组
        this.datasets = Array.isArray(response) ? response : []
      } catch (error) {
        console.error('Load datasets error:', error)
        this.$message.error('加载数据集失败: ' + (error.message || '未知错误'))
        this.datasets = []
      }
    },
    async loadTrainingJobs() {
      try {
        const response = await trainingService.getTrainingJobs()
        // 确保trainingJobs是一个数组
        this.trainingJobs = Array.isArray(response) ? response : []
      } catch (error) {
        console.error('Load training jobs error:', error)
        this.$message.error('加载训练任务失败: ' + (error.message || '未知错误'))
        this.trainingJobs = []
      }
    },
    async startTraining() {
      if (!this.trainingForm.dataset_id) {
        this.$message.warning('请选择数据集')
        return
      }
      
      this.training = true
      this.statusMessage = '训练开始...'
      this.statusType = 'info'
      
      try {
        const response = await trainingService.startTraining(this.trainingForm)
        this.statusMessage = '训练任务已提交'
        this.statusType = 'success'
        
        // 保存当前训练任务ID
        if (response && response.job_id) {
          this.currentJobId = response.job_id
          this.trainingStatus = response.status || 'pending'
          this.startPolling()
        }
      } catch (error) {
        console.error('Training error:', error)
        this.statusMessage = '训练失败: ' + (error.message || '未知错误')
        this.statusType = 'error'
      } finally {
        this.training = false
      }
    },
    async stopTraining() {
      if (!this.currentJobId) {
        this.$message.warning('没有正在进行的训练任务')
        return
      }
      
      try {
        const response = await trainingService.stopTraining(this.currentJobId)
        this.statusMessage = '训练已停止'
        this.statusType = 'warning'
        this.trainingStatus = 'stopped'
        
        // 刷新训练任务列表
        await this.loadTrainingJobs()
      } catch (error) {
        console.error('Stop training error:', error)
        this.$message.error('停止训练失败: ' + (error.message || '未知错误'))
      }
    },
    async pollTrainingStatus() {
      if (!this.currentJobId) return
      
      try {
        const response = await trainingService.getTrainingStatus(this.currentJobId)
        if (response) {
          this.trainingStatus = response.status
          this.trainingProgress = response.progress || 0
          
          // 更新状态消息
          if (response.status === 'running') {
            this.statusMessage = `训练进行中 (${Math.round(this.trainingProgress)}%)`
            this.statusType = 'info'
          } else if (response.status === 'succeeded') {
            this.statusMessage = '训练成功完成'
            this.statusType = 'success'
            this.clearPolling() // 训练完成，停止轮询
          } else if (response.status === 'failed') {
            this.statusMessage = '训练失败: ' + (response.error || '未知错误')
            this.statusType = 'error'
            this.clearPolling() // 训练失败，停止轮询
          } else if (response.status === 'stopped') {
            this.statusMessage = '训练已手动停止'
            this.statusType = 'warning'
            this.clearPolling() // 训练停止，停止轮询
          } else if (response.status === 'pending') {
            this.statusMessage = '训练任务排队中...'
            this.statusType = 'info'
          }
          
          // 更新日志
          if (response.logs) {
            if (Array.isArray(response.logs)) {
              // 处理日志数组，确保每个元素都是字符串
              this.trainingLogs = response.logs.map(log => {
                return typeof log === 'string' ? log : JSON.stringify(log)
              })
              // 确保每个日志条目后面有换行符
              this.trainingLogs = this.trainingLogs.map(log => log.endsWith('\n') ? log : log + '\n')
            } else if (typeof response.logs === 'string') {
              // 适应单个日志字符串的情况
              this.trainingLogs = [response.logs]
            }
          } else if (response.log && typeof response.log === 'string') {
            // 适应单个日志字符串的情况
            this.trainingLogs = [response.log]
          }
          
          // 如果训练已结束，刷新训练任务列表
          if (['succeeded', 'failed', 'stopped'].includes(response.status)) {
            await this.loadTrainingJobs()
          }
        }
      } catch (error) {
        console.error('Status polling error:', error)
        // 轮询出错不要停止，继续尝试
      }
    },
    startPolling() {
      // 清除可能存在的轮询
      this.clearPolling()
      
      // 开始新的轮询，每3秒查询一次状态
      this.pollingInterval = setInterval(() => {
        this.pollTrainingStatus()
      }, 3000)
      
      // 立即执行一次
      this.pollTrainingStatus()
    },
    clearPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },
    async viewJobDetails(jobId) {
      this.currentJobId = jobId
      await this.pollTrainingStatus()
      this.$message.success('已加载任务详情')
    },
    getStatusType(status) {
      const statusMap = {
        'pending': 'info',
        'running': 'primary',
        'succeeded': 'success',
        'failed': 'danger',
        'stopped': 'warning'
      }
      return statusMap[status] || 'info'
    },
    getProgressStatus(status) {
      if (status === 'succeeded') return 'success'
      if (status === 'failed') return 'exception'
      if (status === 'stopped') return 'warning'
      return ''
    }
  }
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