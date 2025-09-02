<template>
  <div class="training">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型训练</span>
        </div>
      </template>
      <div class="content">
        <div class="dataset-selection">
          <el-form :model="trainingForm" label-width="120px">
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
            
            <el-form-item label="训练轮数">
              <el-slider v-model="trainingForm.epochs" :min="1" :max="10" show-input style="width: 100%;" />
            </el-form-item>
            
            <el-form-item label="学习率">
              <el-input-number v-model="trainingForm.learning_rate" :min="1e-6" :max="1e-3" :step="1e-6" :precision="6" />
            </el-form-item>
            
            <el-form-item label="批次大小">
              <el-select v-model="trainingForm.batch_size" placeholder="请选择批次大小">
                <el-option label="4" :value="4" />
                <el-option label="8" :value="8" />
                <el-option label="16" :value="16" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="startTraining" :loading="training">开始训练</el-button>
              <el-button type="danger" @click="stopTraining" :disabled="!currentJobId || trainingStatus !== 'running'">停止训练</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="training-status" v-if="currentJobId">
          <el-alert
            :title="statusMessage"
            :type="statusType"
            show-icon
          />
          
          <div class="progress-container" v-if="trainingStatus === 'running'">
            <h4>训练进度: {{ Math.round(trainingProgress) }}%</h4>
            <el-progress :percentage="trainingProgress" :status="progressStatus" />
          </div>
          
          <div class="logs-container" v-if="trainingLogs.length > 0">
            <h4>训练日志:</h4>
            <el-card class="log-card">
              <pre class="logs">{{ trainingLogs.join('') }}</pre>
            </el-card>
          </div>
        </div>
      </div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>训练任务列表</span>
          <el-button type="primary" size="small" @click="loadTrainingJobs">刷新</el-button>
        </div>
      </template>
      <div class="jobs-list">
        <el-table :data="trainingJobs" style="width: 100%">
          <el-table-column prop="id" label="任务ID" width="80" />
          <el-table-column prop="dataset_id" label="数据集ID" width="100" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress || 0" :status="getProgressStatus(scope.row.status)" />
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="viewJobDetails(scope.row.id)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>可用数据集</span>
        </div>
      </template>
      <div class="dataset-list">
        <el-table :data="datasets" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="created_at" label="创建时间" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import { datasetService, trainingService } from '../services/api'

export default {
  name: 'TrainingView',
  data() {
    return {
      datasets: [],
      trainingForm: {
        dataset_id: '',
        epochs: 3,
        learning_rate: 2e-5,
        batch_size: 16
      },
      training: false,
      statusMessage: '',
      statusType: 'info',
      currentJobId: null,
      trainingStatus: '',
      trainingProgress: 0,
      trainingLogs: [],
      pollingInterval: null,
      trainingJobs: []
    }
  },
  computed: {
    progressStatus() {
      if (this.trainingStatus === 'succeeded') return 'success'
      if (this.trainingStatus === 'failed') return 'exception'
      if (this.trainingStatus === 'stopped') return 'warning'
      return ''
    }
  },
  async mounted() {
    await this.loadDatasets()
    await this.loadTrainingJobs()
    
    // 检查URL参数中是否有datasetId
    const datasetId = this.$route.query.datasetId
    if (datasetId) {
      this.trainingForm.dataset_id = parseInt(datasetId, 10)
    }
  },
  beforeUnmount() {
    // 组件销毁前清除轮询
    this.clearPolling()
  },
  methods: {
    async loadDatasets() {
      try {
        const response = await datasetService.getDatasets()
        if (response.data && response.data.success) {
          this.datasets = response.data.data || []
        } else {
          this.$message.warning('加载数据集失败: ' + (response.data.message || '未知错误'))
        }
      } catch (error) {
        console.error('Load datasets error:', error)
        this.$message.error('加载数据集失败')
      }
    },
    async loadTrainingJobs() {
      try {
        const response = await trainingService.getTrainingJobs()
        if (response.data && response.data.success) {
          this.trainingJobs = response.data.data || []
        }
      } catch (error) {
        console.error('Load training jobs error:', error)
        this.$message.error('加载训练任务失败')
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
        if (response.data && response.data.success) {
          const data = response.data.data
          this.statusMessage = response.data.message || '训练任务已提交'
          this.statusType = 'success'
          
          // 保存当前训练任务ID
          if (data && data.job_id) {
            this.currentJobId = data.job_id
            this.trainingStatus = data.status || 'pending'
            this.startPolling()
          }
        } else {
          this.statusMessage = '训练失败: ' + (response.data.message || '未知错误')
          this.statusType = 'error'
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
        if (response.data && response.data.success) {
          const data = response.data.data
          this.statusMessage = response.data.message || '训练已停止'
          this.statusType = 'warning'
          this.trainingStatus = data.status || 'stopped'
        } else {
          this.$message.error('停止训练失败: ' + (response.data.message || '未知错误'))
        }
      } catch (error) {
        console.error('Stop training error:', error)
        this.$message.error('停止训练失败: ' + (error.message || '未知错误'))
      }
    },
    async pollTrainingStatus() {
      if (!this.currentJobId) return
      
      try {
        const response = await trainingService.getTrainingStatus(this.currentJobId)
        if (response.data && response.data.success) {
          const data = response.data.data
          this.trainingStatus = data.status
          this.trainingProgress = data.progress || 0
          
          // 更新状态消息
          if (data.status === 'running') {
            this.statusMessage = `训练进行中 (${Math.round(this.trainingProgress)}%)`
            this.statusType = 'info'
          } else if (data.status === 'succeeded') {
            this.statusMessage = '训练成功完成'
            this.statusType = 'success'
            this.clearPolling() // 训练完成，停止轮询
          } else if (data.status === 'failed') {
            this.statusMessage = '训练失败'
            this.statusType = 'error'
            this.clearPolling() // 训练失败，停止轮询
          } else if (data.status === 'stopped') {
            this.statusMessage = '训练已手动停止'
            this.statusType = 'warning'
            this.clearPolling() // 训练停止，停止轮询
          }
          
          // 更新日志
          if (data.logs) {
            this.trainingLogs = data.logs
          }
          
          // 如果训练已结束，刷新训练任务列表
          if (['succeeded', 'failed', 'stopped'].includes(data.status)) {
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