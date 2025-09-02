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
              <el-input-number v-model="trainingForm.learning_rate" :min="1e-6" :max="1e-6" :step="1e-6" />
            </el-form-item>
            
            <el-form-item label="批次大小">
              <el-select v-model="trainingForm.batch_size" placeholder="请选择批次大小">
                <el-option label="4" value="4" />
                <el-option label="8" value="8" />
                <el-option label="16" value="16" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="startTraining" 
                :loading="training"
                :disabled="!trainingForm.dataset_id"
              >
                {{ training ? '训练中...' : '开始训练' }}
              </el-button>
              <el-button @click="checkStatus" style="margin-left: 10px;">
                刷新状态
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="training-status" v-if="statusMessage">
          <el-alert
            :title="statusMessage"
            :type="statusType"
            show-icon
          />
        </div>
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
        dataset_id: null,
        epochs: 3,
        learning_rate: 2e-5,
        batch_size: 8
      },
      training: false,
      statusMessage: '',
      statusType: 'info'
    }
  },
  async mounted() {
    await this.loadDatasets()
  },
  methods: {
    async loadDatasets() {
      try {
        const response = await datasetService.getDatasets()
        this.datasets = response.data
      } catch (error) {
        console.error('Load datasets error:', error)
        this.$message.error('加载数据集失败')
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
        console.log('Training response:', response.data)
        this.statusMessage = response.data.message
        this.statusType = response.data.status === 'completed' ? 'success' : 'warning'
      } catch (error) {
        console.error('Training error:', error)
        this.statusMessage = '训练失败: ' + (error.response?.data?.detail || error.message)
        this.statusType = 'error'
      } finally {
        this.training = false
      }
    },
    async checkStatus() {
      try {
        const response = await trainingService.getTrainingStatus()
        this.statusMessage = response.data.message
        this.statusType = response.data.status === 'ready' ? 'success' : 'info'
      } catch (error) {
        console.error('Status check error:', error)
        this.$message.error('获取状态失败')
      }
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
  font-size: 18px;
  font-weight: bold;
}

.training-status {
  margin-top: 20px;
}
</style>