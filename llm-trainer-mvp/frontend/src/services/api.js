import axiosInstance from './axios';

// 统一处理API响应
const handleResponse = (promise) => {
  return promise.then(response => {
    // 统一处理标准格式: { success: true, data: [...] }
    if (response && response.success === true) {
      return response.data || response;
    } else {
      return Promise.reject(response);
    }
  });
};

// 数据集服务
const datasetService = {
  // 上传数据集
  uploadDataset(file) {
    const formData = new FormData();
    formData.append('file', file);
    return handleResponse(axiosInstance.post('/api/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }));
  },

  // 获取所有数据集
  getDatasets() {
    return handleResponse(axiosInstance.get('/api/datasets'));
  },

  // 获取数据集预览
  getDatasetPreview(datasetId, limit = 10) {
    return handleResponse(axiosInstance.get(`/api/datasets/${datasetId}/preview?limit=${limit}`));
  }
};

// 训练服务
const trainingService = {
  // 开始训练
  startTraining(trainingParams) {
    return handleResponse(axiosInstance.post('/api/train/start', trainingParams));
  },

  // 获取训练状态
  getTrainingStatus(jobId) {
    if (!jobId) {
      throw new Error('需要提供job_id参数');
    }
    return handleResponse(axiosInstance.get(`/api/train/status/${jobId}`));
  },

  // 停止训练
  stopTraining(jobId) {
    return handleResponse(axiosInstance.post('/api/train/stop', { job_id: jobId }));
  },

  // 获取训练日志
  getTrainingLogs(jobId, lines = 50) {
    return handleResponse(axiosInstance.get(`/api/train/logs/${jobId}?lines=${lines}`));
  },

  // 获取所有训练任务
  getTrainingJobs() {
    return handleResponse(axiosInstance.get('/api/train/jobs'));
  }
};

// 预测服务
const predictionService = {
  // 文本分类预测
  predict(text, modelId = null) {
    const payload = { text };
    if (modelId) {
      payload.model_id = modelId;
    }
    return handleResponse(axiosInstance.post('/api/predict', payload));
  }
};

export {
  datasetService,
  trainingService,
  predictionService
};