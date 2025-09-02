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
          </el-form-item>
        </el-form>
        
        <div class="prediction-result" v-if="predictionResult">
          <el-divider />
          <h3>预测结果</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="预测类别">
              {{ predictionResult.predicted_class }}
            </el-descriptions-item>
            <el-descriptions-item label="置信度">
              {{ (predictionResult.confidence * 100).toFixed(2) }}%
            </el-descriptions-item>
          </el-descriptions>
          <div class="result-text">
            <p>输入文本: {{ predictionResult.text }}</p>
          </div>
        </div>
      </div>
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
          <li>在上方输入框中输入需要分类的文本</li>
          <li>点击"开始预测"按钮</li>
          <li>查看模型预测结果和置信度</li>
        </ol>
        <el-alert
          title="注意"
          type="info"
          description="此功能需要先完成模型训练才能使用。"
          show-icon
          style="margin-top: 15px;"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { predictionService } from '../services/api'

export default {
  name: 'PredictionView',
  data() {
    return {
      predictionForm: {
        text: ''
      },
      predicting: false,
      predictionResult: null
    }
  },
  methods: {
    async predict() {
      if (!this.predictionForm.text) {
        this.$message.warning('请输入文本')
        return
      }
      
      this.predicting = true
      this.predictionResult = null
      
      try {
        const response = await predictionService.predict(this.predictionForm.text)
        console.log('Prediction response:', response.data)
        this.predictionResult = response.data
        this.$message.success('预测完成')
      } catch (error) {
        console.error('Prediction error:', error)
        this.$message.error('预测失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.predicting = false
      }
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