import axiosInstance from './axios'

// 数据集服务
const datasetService = {
  // 上传数据集
  uploadDataset(file) {
    const formData = new FormData()
    formData.append('file', file)
    return axiosInstance.post('/api/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 获取所有数据集
  getDatasets() {
    return axiosInstance.get('/api/datasets')
  },

  // 获取数据集预览
  getDatasetPreview(datasetId, limit = 10) {
    return axiosInstance.get(`/api/datasets/${datasetId}/preview?limit=${limit}`)
  }
}

// 训练服务
const trainingService = {
  // 开始训练
  startTraining(trainingParams) {
    return axiosInstance.post('/api/train/start', trainingParams)
  },
  
  // 获取训练状态
  getTrainingStatus(jobId) {
    if (!jobId) {
      throw new Error('需要提供job_id参数')
    }
    return axiosInstance.get(`/api/train/status/${jobId}`)
  },
  
  // 停止训练
  stopTraining(jobId) {
    return axiosInstance.post('/api/train/stop', { job_id: jobId })
  },

  // 获取训练日志
  getTrainingLogs(jobId, lines = 50) {
    return axiosInstance.get(`/api/train/logs/${jobId}?lines=${lines}`)
  },

  // 获取所有训练任务
  getTrainingJobs() {
    return axiosInstance.get('/api/train/jobs')
  }
}

// 预测服务
const predictionService = {
  // 文本分类预测
  predict(modelId, text) {
    return axiosInstance.post('/api/predict', { model_id: modelId, text })
  }
}

export {
  datasetService,
  trainingService,
  predictionService
}