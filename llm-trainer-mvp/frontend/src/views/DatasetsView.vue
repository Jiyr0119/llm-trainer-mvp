<template>
  <div class="datasets">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据集管理</span>
          <el-button type="primary" size="small" @click="$router.push('/upload')">
            上传新数据集
          </el-button>
        </div>
      </template>
      
      <div class="content">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <div v-else-if="datasets.length === 0" class="empty-data">
          <el-empty description="暂无数据集" />
          <el-button type="primary" @click="$router.push('/upload')">
            上传数据集
          </el-button>
        </div>
        
        <div v-else>
          <el-table :data="datasets" style="width: 100%" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="数据集名称" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="previewDataset(scope.row.id)"
                >
                  预览
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="goToTraining(scope.row.id)"
                >
                  训练
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
    
    <!-- 数据集预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="数据集预览"
      width="70%"
    >
      <div v-if="previewLoading" class="preview-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else>
        <p class="preview-info">显示前 {{ previewData.length }} 条记录</p>
        <el-table :data="previewData" style="width: 100%" border max-height="400px">
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="text" label="文本" show-overflow-tooltip />
          <el-table-column prop="label" label="标签" width="100" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { datasetService } from '../services/api'

export default {
  name: 'DatasetsView',
  data() {
    return {
      datasets: [],
      loading: true,
      previewDialogVisible: false,
      previewLoading: false,
      previewData: [],
      currentDatasetId: null
    }
  },
  created() {
    this.fetchDatasets()
  },
  methods: {
    async fetchDatasets() {
      this.loading = true
      try {
        const response = await datasetService.getDatasets()
        this.datasets = response.data.datasets || response.data || []
      } catch (error) {
        console.error('Failed to fetch datasets:', error)
        this.$message.error('获取数据集列表失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading = false
      }
    },
    async previewDataset(datasetId) {
      this.currentDatasetId = datasetId
      this.previewDialogVisible = true
      this.previewLoading = true
      this.previewData = []
      
      try {
        const response = await datasetService.getDatasetPreview(datasetId)
        this.previewData = response.data.preview || response.data || []
      } catch (error) {
        console.error('Failed to preview dataset:', error)
        this.$message.error('获取数据集预览失败: ' + (error.message || '未知错误'))
      } finally {
        this.previewLoading = false
      }
    },
    goToTraining(datasetId) {
      this.$router.push({
        path: '/train',
        query: { datasetId }
      })
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.datasets {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container,
.empty-data {
  padding: 20px;
  text-align: center;
}

.empty-data .el-button {
  margin-top: 15px;
}

.preview-loading {
  padding: 20px;
}

.preview-info {
  margin-bottom: 15px;
  color: #606266;
  font-size: 14px;
}
</style>