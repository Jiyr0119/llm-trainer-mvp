<template>
  <!-- 推理页面主容器 -->
  <div class="prediction">
    <!-- 推理表单卡片 -->
    <el-card>
      <template #header>
        <!-- 卡片标题 -->
        <div class="card-header">
          <span>模型推理</span>
        </div>
      </template>
      <div class="content">
        <!-- 推理表单，双向绑定到predictionForm数据对象 -->
        <el-form :model="predictionForm" label-width="120px">
          <!-- 模型选择下拉框 -->
          <el-form-item label="选择模型">
            <el-select 
              v-model="predictionForm.modelId" 
              placeholder="选择模型（默认使用最新模型）"
              clearable  <!-- 允许清除选择，使用默认模型 -->
            >
              <!-- 动态生成模型选项 -->
              <el-option 
                v-for="model in trainedModels" 
                :key="model.id" 
                :label="`${model.model_name} (ID: ${model.id})`" 
                :value="model.id"
              />
            </el-select>
          </el-form-item>
          
          <!-- 文本输入区域 -->
          <el-form-item label="输入文本">
            <el-input
              v-model="predictionForm.text"
              type="textarea"
              :rows="4"
              placeholder="请输入要分类的文本"
            />
          </el-form-item>
          
          <!-- 操作按钮区域 -->
          <el-form-item>
            <!-- 预测按钮：根据predicting状态显示不同文本，无文本时禁用 -->
            <el-button 
              type="primary" 
              @click="predict" 
              :loading="predicting"
              :disabled="!predictionForm.text"
            >
              {{ predicting ? '预测中...' : '开始预测' }}
            </el-button>
            <!-- 清空按钮 -->
            <el-button @click="clearForm">清空</el-button>
          </el-form-item>
        </el-form>
        
        <!-- 预测结果区域，仅在有结果时显示 -->
        <div class="prediction-result" v-if="predictionResult">
          <el-divider /> <!-- 分隔线 -->
          <h3>预测结果</h3>
          <!-- 结果详情展示 -->
          <el-descriptions :column="1" border>
            <!-- 预测类别项：根据结果显示不同颜色的标签 -->
            <el-descriptions-item label="预测类别">
              <el-tag :type="predictionResult.predicted_class === '正面' ? 'success' : 'danger'">
                {{ predictionResult.predicted_class }}
              </el-tag>
            </el-descriptions-item>
            <!-- 置信度项：使用进度条直观显示 -->
            <el-descriptions-item label="置信度">
              <el-progress 
                :percentage="Math.round(predictionResult.confidence * 100)" 
                :status="predictionResult.predicted_class === '正面' ? 'success' : 'exception'"
              />
            </el-descriptions-item>
            <!-- 处理时间项：显示模型推理耗时 -->
            <el-descriptions-item label="处理时间">
              {{ predictionResult.processing_time.toFixed(3) }} 秒
            </el-descriptions-item>
          </el-descriptions>
          <!-- 显示输入的原始文本 -->
          <div class="result-text">
            <p>输入文本: {{ predictionResult.text }}</p>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 历史记录卡片，仅在有历史记录时显示 -->
    <el-card style="margin-top: 20px;" v-if="predictionHistory.length > 0">
      <template #header>
        <!-- 卡片标题和操作区 -->
        <div class="card-header">
          <span>预测历史</span>
          <el-button type="text" @click="clearHistory">清空历史</el-button>
        </div>
      </template>
      <!-- 历史记录表格 -->
      <el-table :data="predictionHistory" style="width: 100%">
        <!-- 文本列：显示预测过的文本，过长时显示提示 -->
        <el-table-column prop="text" label="文本" width="300" show-overflow-tooltip />
        <!-- 预测类别列：使用不同颜色标签区分 -->
        <el-table-column prop="predicted_class" label="预测类别" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.predicted_class === '正面' ? 'success' : 'danger'">
              {{ scope.row.predicted_class }}
            </el-tag>
          </template>
        </el-table-column>
        <!-- 置信度列：使用进度条直观显示 -->
        <el-table-column prop="confidence" label="置信度" width="150">
          <template #default="scope">
            <el-progress 
              :percentage="Math.round(scope.row.confidence * 100)" 
              :status="scope.row.predicted_class === '正面' ? 'success' : 'exception'"
            />
          </template>
        </el-table-column>
        <!-- 操作列：提供重用文本功能 -->
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="text" @click="reuseText(scope.row.text)">重新使用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 使用说明卡片 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <!-- 卡片标题 -->
        <div class="card-header">
          <span>使用说明</span>
        </div>
      </template>
      <!-- 使用说明内容 -->
      <div class="instructions">
        <p>在本页面可以测试训练好的模型效果：</p>
        <!-- 使用步骤列表 -->
        <ol>
          <li>选择要使用的模型（可选，默认使用最新训练的模型）</li>
          <li>在输入框中输入需要分类的文本</li>
          <li>点击"开始预测"按钮</li>
          <li>查看模型预测结果和置信度</li>
        </ol>
        <!-- 提示信息 -->
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
// 导入API服务
import { predictionService, trainingService } from '../services/api'

export default {
  name: 'PredictionView', // 组件名称
  data() {
    return {
      // 预测表单数据
      predictionForm: {
        text: '', // 输入文本
        modelId: null // 选择的模型ID，null表示使用默认模型
      },
      predicting: false, // 预测状态标志，控制加载状态
      predictionResult: null, // 预测结果对象
      predictionHistory: [], // 预测历史记录数组
      trainedModels: [] // 已训练模型列表
    }
  },
  // 组件创建时的生命周期钩子
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
  // 组件方法
  methods: {
    // 加载已训练完成的模型列表
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
    // 执行预测操作
    async predict() {
      // 验证输入
      if (!this.predictionForm.text) {
        this.$message.warning('请输入文本')
        return
      }
      
      // 设置加载状态
      this.predicting = true
      
      try {
        // 调用预测API
        const response = await predictionService.predict(
          this.predictionForm.text,
          this.predictionForm.modelId
        )
        
        console.log('Prediction response:', response.data)
        // 保存预测结果
        this.predictionResult = response.data
        
        // 添加到历史记录
        this.addToHistory(this.predictionResult)
        
        // 显示成功消息
        this.$message.success('预测完成')
      } catch (error) {
        // 错误处理
        console.error('Prediction error:', error)
        this.$message.error('预测失败: ' + (error.response?.data?.message || error.message))
      } finally {
        // 无论成功失败，都重置加载状态
        this.predicting = false
      }
    },
    clearForm() {
      this.predictionForm.text = ''
      this.predictionResult = null
    },
    // 添加预测结果到历史记录
    addToHistory(result) {
      // 添加时间戳
      const historyItem = {
        ...result,
        timestamp: new Date().toISOString()
      }
      
      // 添加到历史记录开头（最新的记录显示在最前面）
      this.predictionHistory.unshift(historyItem)
      
      // 限制历史记录数量，最多保留10条
      if (this.predictionHistory.length > 10) {
        this.predictionHistory = this.predictionHistory.slice(0, 10)
      }
      
      // 保存到本地存储，以便页面刷新后仍能保留历史记录
      localStorage.setItem('predictionHistory', JSON.stringify(this.predictionHistory))
    },
    // 清空所有历史记录
    clearHistory() {
      this.predictionHistory = []
      // 同时从本地存储中移除
      localStorage.removeItem('predictionHistory')
      // 显示成功消息
      this.$message.success('历史记录已清空')
    },
    // 重新使用历史记录中的文本
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