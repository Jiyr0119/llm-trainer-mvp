<template>
  <div class="home">
    <div class="home-background"></div>
    <el-card class="welcome-card">
      <div class="card-header">
        <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="logo" />
        <h1>欢迎使用大语言模型训练平台</h1>
        <p class="subtitle">简化AI模型训练流程，提升开发效率</p>
      </div>
      <div class="content">
        <div class="intro-section">
          <h2>平台功能</h2>
          <p>这是一个简化版的MVP实现，展示了本地大语言模型训练的核心功能：</p>
          <div class="feature-list">
            <div class="feature-item">
              <div class="feature-icon upload-icon">
                <el-icon><Upload /></el-icon>
              </div>
              <div class="feature-text">
                <h3>上传文本分类数据集</h3>
                <p>轻松上传和管理您的训练数据</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon train-icon">
                <el-icon><CPU /></el-icon>
              </div>
              <div class="feature-text">
                <h3>使用BERT模型进行微调训练</h3>
                <p>高效训练定制化语言模型</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon predict-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="feature-text">
                <h3>模型推理演示</h3>
                <p>实时测试和验证模型效果</p>
              </div>
            </div>
          </div>
        </div>
        
        <el-alert
          title="注意"
          type="warning"
          description="此MVP版本仅用于演示核心功能流程，在生产环境中需要更多优化和安全措施。"
          show-icon
          class="notice-alert"
        />
        
        <div class="actions">
          <el-button type="primary" @click="goToUpload" class="action-btn upload-btn">
            <el-icon><Upload /></el-icon>
            开始上传数据集
          </el-button>
          <el-button @click="goToTraining" class="action-btn train-btn">
            <el-icon><CPU /></el-icon>
            查看训练功能
          </el-button>
          <el-button @click="goToPrediction" class="action-btn predict-btn">
            <el-icon><DataAnalysis /></el-icon>
            测试模型推理
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToUpload() {
  router.push('/upload')
}

function goToTraining() {
  router.push('/train')
}

function goToPrediction() {
  router.push('/predict')
}
</script>

<style scoped>
.home {
  position: relative;
  padding: 40px 20px;
  min-height: calc(100vh - 120px);
  overflow: hidden;
}

.home-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4ecfb 100%);
  z-index: -1;
}

.welcome-card {
  max-width: 900px;
  margin: 0 auto;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: none;
  transition: transform 0.3s, box-shadow 0.3s;
}

.welcome-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.card-header {
  text-align: center;
  padding: 30px 20px;
  background: linear-gradient(135deg, #4158D0 0%, #C850C0 100%);
  border-bottom: none;
  color: white;
}

.logo {
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
}

.card-header h1 {
  font-size: 28px;
  color: white;
  margin-bottom: 10px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin-top: 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.content {
  padding: 30px;
  text-align: left;
}

.intro-section {
  margin-bottom: 30px;
}

.intro-section h2 {
  font-size: 22px;
  background: linear-gradient(45deg, #4158D0, #C850C0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 15px;
  font-weight: 600;
  display: inline-block;
}

.feature-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px 0;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 20px;
  border-radius: 12px;
  flex: 1 1 250px;
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.9);
}

.feature-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  border-radius: 12px;
  margin-right: 15px;
  flex-shrink: 0;
}

.feature-icon .el-icon {
  font-size: 24px;
  color: white;
}

.upload-icon {
  background: linear-gradient(135deg, #4158D0, #6C7FD8);
}

.train-icon {
  background: linear-gradient(135deg, #6C7FD8, #C850C0);
}

.predict-icon {
  background: linear-gradient(135deg, #C850C0, #FF6CAB);
}

.feature-text h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #303133;
}

.feature-text p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.notice-alert {
  margin: 25px 0;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.action-btn {
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  border-radius: 8px;
  font-weight: 500;
  border: none;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.action-btn .el-icon {
  font-size: 18px;
}

.upload-btn {
  background: linear-gradient(135deg, #4158D0, #6C7FD8);
  color: white;
}

.upload-btn:hover {
  background: linear-gradient(135deg, #3a4ec0, #5b6ec7);
}

.train-btn {
  background: linear-gradient(135deg, #6C7FD8, #C850C0);
  color: white;
}

.train-btn:hover {
  background: linear-gradient(135deg, #5b6ec7, #b745af);
}

.predict-btn {
  background: linear-gradient(135deg, #C850C0, #FF6CAB);
  color: white;
}

.predict-btn:hover {
  background: linear-gradient(135deg, #b745af, #ff5ba0);
}

@media (max-width: 768px) {
  .feature-list {
    flex-direction: column;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>