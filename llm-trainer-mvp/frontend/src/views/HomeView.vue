<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用大语言模型训练平台</span>
        </div>
      </template>
      <div class="content">
        <p>这是一个简化版的MVP实现，展示了本地大语言模型训练的核心功能：</p>
        <ul>
          <li>上传文本分类数据集</li>
          <li>使用BERT模型进行微调训练</li>
          <li>模型推理演示</li>
        </ul>
        <el-alert
          title="注意"
          type="warning"
          description="此MVP版本仅用于演示核心功能流程，在生产环境中需要更多优化和安全措施。"
          show-icon
          style="margin: 20px 0;"
        />
        <div class="actions">
          <el-button type="primary" @click="goToUpload">开始上传数据集</el-button>
          <el-button @click="goToTraining">查看训练功能</el-button>
          <el-button @click="goToPrediction">测试模型推理</el-button>
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
.welcome-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.content {
  text-align: left;
}

.content ul {
  margin: 10px 0 20px 20px;
}

.content li {
  margin: 8px 0;
}

.actions {
  text-align: center;
  margin-top: 20px;
}

.actions .el-button {
  margin: 0 10px;
}
</style>