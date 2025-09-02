import axios from 'axios'

const API_BASE = '/api'

export const datasetService = {
  // 上传数据集
  async uploadDataset(file) {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post(`${API_BASE}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 获取数据集列表
  async getDatasets() {
    return axios.get(`${API_BASE}/datasets`)
  }
}

export const trainingService = {
  // 开始训练
  async startTraining(trainingRequest) {
    return axios.post(`${API_BASE}/train`, trainingRequest)
  },
  
  // 获取训练状态
  async getTrainingStatus() {
    return axios.get(`${API_BASE}/train/status`)
  }
}

export const predictionService = {
  // 模型预测
  async predict(text) {
    return axios.post(`${API_BASE}/predict`, { text })
  }
}