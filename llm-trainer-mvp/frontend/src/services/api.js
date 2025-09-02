import axiosInstance from './axios'

// 数据集服务
const datasetService = {
  // 上传数据集
  uploadDataset(file) {
    const formData = new FormData()
    formData.append('file', file)
    return axiosInstance.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 获取所有数据集
  getDatasets() {
    return axiosInstance.get('/datasets')
  },

  // 获取数据集预览
  getDatasetPreview(datasetId, limit = 10) {
    return axiosInstance.get(`/dataset/preview/${datasetId}?limit=${limit}`)
  }
}

// 训练服务
const trainingService = {
  // 开始训练
  startTraining(trainingParams) {
    return axiosInstance.post('/train', trainingParams)
  },
  
  // 获取训练状态
  getTrainingStatus(jobId) {
    const url = jobId ? `/train/status/${jobId}` : '/train/status'
    return axiosInstance.get(url)
  },
  
  // 停止训练
  stopTraining(jobId) {
    return axiosInstance.post(`/train/stop`, { job_id: jobId })
  }
}

// 预测服务
const predictionService = {
  // 文本分类预测
  predict(text) {
    return axiosInstance.post('/predict', { text })
  }
}

export {
  datasetService,
  trainingService,
  predictionService
}