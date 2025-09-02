<template>
  <div class="prediction">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型推理</span>
        </div>
      </template>
      <div class="content">
        <el-form :model="predictionForm" label-width="120px">
          <el-form-item label="选择模型">
            <el-select 
              v-model="predictionForm.modelId" 
              placeholder="选择模型（默认使用最新模型）"
              clearable
            >
              <el-option 
                v-for="model in trainedModels" 
                :key="model.id" 
                :label="`${model.model_name} (ID: ${model.id})`" 
                :value="model.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="输入文本">
            <el-input
              v-model="predictionForm.text"
              type="textarea"
              :rows="4"
              placeholder="请输入要分类的文本"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="predict" 
              :loading="predicting"
              :disabled="!predictionForm.text"
            >
              {{ predicting ? '预测中...' : '开始预测' }}
            </el-button>
            <el-button @click="clearForm">清空</el-button>
          </el-form-item>
        </el-form>
        
        <div class="prediction-result" v-if="predictionResult">
          <el-divider />
          <h3>预测结果</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="预测类别">
              <el-tag :type="predictionResult.predicted_class === '正面' ? 'success' : 'danger'">
                {{ predictionResult.predicted_class }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="置信度">
              <el-progress 
                :percentage="Math.round(predictionResult.confidence * 100)" 
                :status="predictionResult.predicted_class === '正面' ? 'success' : 'exception'"
              />
            </el-descriptions-item>
            <el-descriptions-item label="处理时间">
              {{ predictionResult.processing_time.toFixed(3) }} 秒
            </el-descriptions-item>
          </el-descriptions>
          <div class="result-text">
            <p>输入文本: {{ predictionResult.text }}</p>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 历史记录 -->
    <el-card style="margin-top: 20px;" v-if="predictionHistory.length > 0">
      <template #header>
        <div class="card-header">
          <span>预测历史</span>
          <el-button type="text" @click="clearHistory">清空历史</el-button>
        </div>
      </template>
      <el-table :data="predictionHistory" style="width: 100%">
        <el-table-column prop="text" label="文本" width="300" show-overflow-tooltip />
        <el-table-column prop="predicted_class" label="预测类别" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.predicted_class === '正面' ? 'success' : 'danger'">
              {{ scope.row.predicted_class }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="150">
          <template #default="scope">
            <el-progress 
              :percentage="Math.round(scope.row.confidence * 100)" 
              :status="scope.row.predicted_class === '正面' ? 'success' : 'exception'"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="text" @click="reuseText(scope.row.text)">重新使用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>使用说明</span>
        </div>
      </template>
      <div class="instructions">
        <p>在本页面可以测试训练好的模型效果：</p>
        <ol>
          <li>选择要使用的模型（可选，默认使用最新训练的模型）</li>
          <li>在输入框中输入需要分类的文本</li>
          <li>点击"开始预测"按钮</li>
          <li>查看模型预测结果和置信度</li>
        </ol>
        <el-alert
          title="注意"
          type="info"
          description="此功能需要先完成模型训练才能使用。如果没有训练好的模型，系统将使用默认预训练模型进行推理。"
          show-icon
          style="margin-top: 15px;"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { predictionService, trainingService } from '../services/api'

export default {
  name: 'PredictionView',
  data() {
    return {
      predictionForm: {
        text: '',
        modelId: null
      },
      predicting: false,
      predictionResult: null,
      predictionHistory: [],
      trainedModels: []
    }
  },
  created() {
    // 从本地存储加载历史记录
    const savedHistory = localStorage.getItem('predictionHistory')
    if (savedHistory) {
      try {
        this.predictionHistory = JSON.parse(savedHistory)
      } catch (e) {
        console.error('Failed to parse prediction history:', e)
      }
    }
    
    // 加载训练好的模型列表
    this.loadTrainedModels()
  },
  methods: {
    async loadTrainedModels() {
      try {
        const response = await trainingService.getTrainingJobs()
        // 只显示训练成功的模型
        this.trainedModels = response.data.filter(job => job.status === 'completed')
      } catch (error) {
        console.error('Failed to load trained models:', error)
        this.$message.error('加载模型列表失败')
      }
    },
    async predict() {
      if (!this.predictionForm.text) {
        this.$message.warning('请输入文本')
        return
      }
      
      this.predicting = true
      
      try {
        const response = await predictionService.predict(
          this.predictionForm.text,
          this.predictionForm.modelId
        )
        
        console.log('Prediction response:', response.data)
        this.predictionResult = response.data
        
        // 添加到历史记录
        this.addToHistory(this.predictionResult)
        
        this.$message.success('预测完成')
      } catch (error) {
        console.error('Prediction error:', error)
        this.$message.error('预测失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.predicting = false
      }
    },
    clearForm() {
      this.predictionForm.text = ''
      this.predictionResult = null
    },
    addToHistory(result) {
      // 添加时间戳
      const historyItem = {
        ...result,
        timestamp: new Date().toISOString()
      }
      
      // 添加到历史记录开头
      this.predictionHistory.unshift(historyItem)
      
      // 限制历史记录数量
      if (this.predictionHistory.length > 10) {
        this.predictionHistory = this.predictionHistory.slice(0, 10)
      }
      
      // 保存到本地存储
      localStorage.setItem('predictionHistory', JSON.stringify(this.predictionHistory))
    },
    clearHistory() {
      this.predictionHistory = []
      localStorage.removeItem('predictionHistory')
      this.$message.success('历史记录已清空')
    },
    reuseText(text) {
      this.predictionForm.text = text
      this.predictionResult = null
      // 滚动到顶部
      window.scrollTo(0, 0)
    }
  }
}
</script>

<style scoped>
.prediction {
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

.prediction-result {
  margin-top: 20px;
}

.result-text {
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.instructions ol {
  margin: 10px 0 0 20px;
}

.instructions li {
  margin: 5px 0;
}
</style>