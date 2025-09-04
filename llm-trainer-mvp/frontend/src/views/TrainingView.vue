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
      if (this.trainingStatus === 'succeeded' || this.trainingStatus === 'completed') return 'success' // 成功状态
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
        // 直接使用datasetService.getDatasets()，不再需要适配器
        this.datasets = await datasetService.getDatasets()
      } catch (error) {
        console.error('Load datasets error:', error)
        this.$message.error('加载数据集失败: ' + (error.message || '未知错误'))
        this.datasets = []
      }
    },
    async loadTrainingJobs() {
      try {
        // 直接使用trainingService.getTrainingJobs()，不再需要适配器
        this.trainingJobs = await trainingService.getTrainingJobs()
      } catch (error) {
        console.error('Load training jobs error:', error)
        this.$message.error('加载训练任务列表失败: ' + (error.message || '未知错误'))
        this.trainingJobs = []
      }
    },
    // 开始训练方法
    async startTraining() {
      // 表单验证：检查是否选择了数据集
      if (!this.trainingForm.dataset_id) {
        this.$message.warning('请选择一个数据集')
        return
      }
      
      // 设置训练状态为进行中
      this.training = true
      this.statusMessage = '正在启动训练任务...'
      this.statusType = 'info'
      
      try {
        // 调用训练服务开始训练，传递训练参数
        const result = await trainingService.startTraining(this.trainingForm)
        
        // 保存返回的任务ID并初始化状态
        this.currentJobId = result.job_id
        this.trainingStatus = 'pending'
        this.trainingProgress = 0
        this.trainingLogs = []
        
        // 更新状态消息
        this.statusMessage = '训练任务已启动'
        this.statusType = 'success'
        
        // 启动轮询获取训练状态
        this.startPolling()
        
        // 重新加载训练任务列表以显示新任务
        await this.loadTrainingJobs()
      } catch (error) {
        // 处理训练启动失败的情况
        console.error('Start training error:', error)
        this.statusMessage = '训练任务启动失败: ' + (error.message || '未知错误')
        this.statusType = 'error'
        this.$message.error(this.statusMessage)
      } finally {
        // 重置训练状态标志
        this.training = false
      }
    },
    // 停止训练方法
    async stopTraining() {
      // 检查是否有当前任务ID
      if (!this.currentJobId) {
        this.$message.warning('没有正在运行的训练任务')
        return
      }
      
      try {
        // 调用训练服务停止训练，传递任务ID
        await trainingService.stopTraining(this.currentJobId)
        
        // 更新状态消息
        this.statusMessage = '已发送停止训练请求'
        this.statusType = 'info'
        this.$message.success('停止训练请求已发送')
        
        // 停止轮询
        this.clearPolling()
      } catch (error) {
        // 处理停止训练失败的情况
        console.error('Stop training error:', error)
        this.$message.error('停止训练失败: ' + (error.message || '未知错误'))
      }
    },
    // 获取训练状态方法
    async getTrainingStatus() {
      // 检查是否有当前任务ID
      if (!this.currentJobId) return
      
      try {
        // 调用训练服务获取训练状态，传递任务ID
        const status = await trainingService.getTrainingStatus(this.currentJobId)
        
        // 更新组件状态数据
        this.trainingStatus = status.status
        this.trainingProgress = status.progress || 0
        
        // 根据训练状态更新状态消息和类型
        switch (status.status) {
          case 'pending':
            this.statusMessage = '训练任务正在等待中...'
            this.statusType = 'info'
            break
          case 'running':
            this.statusMessage = '训练进行中...'
            this.statusType = 'info'
            break
          case 'succeeded':
          case 'completed':  // 添加对completed状态的支持
            this.statusMessage = '训练已完成'
            this.statusType = 'success'
            // 训练完成后停止轮询
            this.clearPolling()
            // 重新加载训练任务列表以更新状态
            setTimeout(() => {
              this.loadTrainingJobs()
            }, 1000) // 延迟1秒再加载，避免过于频繁的请求
            break
          case 'failed':
            this.statusMessage = '训练失败: ' + (status.error || '未知错误')
            this.statusType = 'error'
            // 训练失败后停止轮询
            this.clearPolling()
            // 延迟加载训练任务列表
            setTimeout(() => {
              this.loadTrainingJobs()
            }, 1000) // 延迟1秒再加载
            break
          case 'stopped':
            this.statusMessage = '训练已停止'
            this.statusType = 'warning'
            // 训练停止后停止轮询
            this.clearPolling()
            // 延迟加载训练任务列表
            setTimeout(() => {
              this.loadTrainingJobs()
            }, 1000) // 延迟1秒再加载
            break
        }
      } catch (error) {
        // 处理获取训练状态失败的情况
        console.error('Get training status error:', error)
        this.statusMessage = '获取训练状态失败: ' + (error.message || '未知错误')
        this.statusType = 'error'
      }
    },
    // 获取训练日志方法
    async getTrainingLogs() {
      // 检查是否有当前任务ID
      if (!this.currentJobId) return
      
      try {
        // 调用训练服务获取训练日志，传递任务ID和行数参数
        const logs = await trainingService.getTrainingLogs(this.currentJobId, 50)
        // 更新组件日志数据
        this.trainingLogs = logs || []
      } catch (error) {
        // 处理获取训练日志失败的情况
        console.error('Get training logs error:', error)
        this.$message.error('获取训练日志失败: ' + (error.message || '未知错误'))
      }
    },
    // 启动轮询方法
    startPolling() {
      // 先清除现有的轮询定时器（如果有）
      this.clearPolling()
      
      // 设置新的轮询定时器，每2秒获取一次训练状态和日志
      this.pollingInterval = setInterval(async () => {
        await this.getTrainingStatus()
        await this.getTrainingLogs()
      }, 2000)
    },
    // 清除轮询方法
    clearPolling() {
      // 检查并清除轮询定时器
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },
    // 查看任务详情方法
    async viewJobDetails(jobId) {
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
        this.$alert(details, '任务详情', {
          confirmButtonText: '确定',
          customClass: 'job-details-dialog'
        })
      } catch (error) {
        // 处理获取任务详情失败的情况
        console.error('View job details error:', error)
        this.$message.error('获取任务详情失败: ' + (error.message || '未知错误'))
      }
    },
    // 根据任务状态返回对应标签类型的方法
    getStatusType(status) {
      const statusTypes = {
        pending: 'info',
        running: 'primary',
        succeeded: 'success',
        completed: 'success',  // 添加对completed状态的支持
        failed: 'danger',
        stopped: 'warning'
      }
      return statusTypes[status] || 'info'
    },
    
    // 根据任务状态返回对应进度条状态的方法
    getProgressStatus(status) {
      const progressStatuses = {
        succeeded: 'success',
        completed: 'success',  // 添加对completed状态的支持
        failed: 'exception',
        stopped: 'warning'
      }
      return progressStatuses[status] || ''
    }
  }
};
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