<template>
  <div class="upload">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据集上传</span>
        </div>
      </template>
      <div class="content">
        <el-upload
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".csv"
        >
          <el-icon class="el-icon--upload">
            <upload-filled />
          </el-icon>
          <div class="el-upload__text">
            将CSV文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              请上传CSV格式文件，包含text和label两列
            </div>
          </template>
        </el-upload>
        
        <div v-if="selectedFile" class="file-info">
          <p>已选择文件: {{ selectedFile.name }}</p>
          <el-button type="primary" @click="uploadDataset" :loading="uploading">
            {{ uploading ? '上传中...' : '确认上传' }}
          </el-button>
        </div>
        
        <div v-if="uploadSuccess" class="success-message">
          <el-alert
            title="上传成功"
            type="success"
            description="数据集已成功上传，可以开始训练了。"
            show-icon
          />
          <el-button type="success" @click="goToTraining" style="margin-top: 15px;">
            前往训练页面
          </el-button>
        </div>
      </div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据格式说明</span>
        </div>
      </template>
      <div class="format-info">
        <p>请确保您的CSV文件具有以下格式：</p>
        <pre>
text,label
"今天天气很好",1
"我很不开心",0
"这个产品不错",1
        </pre>
        <p>注意事项：</p>
        <ul>
          <li>必须包含text和label两个列</li>
          <li>label应为数字（0或1）</li>
          <li>文本内容可以是任意长度的中文或英文</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script>
import { UploadFilled } from '@element-plus/icons-vue'
import { datasetService } from '../services/api'

export default {
  name: 'UploadView',
  components: {
    UploadFilled
  },
  data() {
    return {
      selectedFile: null,
      uploading: false,
      uploadSuccess: false
    }
  },
  methods: {
    handleFileChange(file) {
      this.selectedFile = file.raw
    },
    handleFileRemove() {
      this.selectedFile = null
      this.uploadSuccess = false
    },
    async uploadDataset() {
      if (!this.selectedFile) {
        this.$message.warning('请先选择文件')
        return
      }
      
      this.uploading = true
      try {
        const response = await datasetService.uploadDataset(this.selectedFile)
        console.log('Upload response:', response.data)
        this.uploadSuccess = true
        this.$message.success('数据集上传成功')
      } catch (error) {
        console.error('Upload error:', error)
        this.$message.error('上传失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.uploading = false
      }
    },
    goToTraining() {
      this.$router.push('/train')
    }
  }
}
</script>

<style scoped>
.upload {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.file-info {
  margin-top: 20px;
  text-align: center;
}

.success-message {
  margin-top: 20px;
  text-align: center;
}

.format-info pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.format-info ul {
  margin: 10px 0 0 20px;
}

.format-info li {
  margin: 5px 0;
}
</style>