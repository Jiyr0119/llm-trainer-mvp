import axiosInstance from './axios';
import { datasetAdapter, trainingAdapter, predictionAdapter } from './adapters';

// 统一处理API响应
const handleResponse = (promise) => {
  return promise.then(response => {
    // 后端统一返回格式：{ success: true, code: 200, message: "...", data: [...] }
    if (response && response.success === true) {
      // 成功响应，返回data部分
      return response.data;
    } else if (response && response.success === false) {
      // 失败响应，抛出错误
      return Promise.reject({
        success: false,
        message: response.message || '操作失败',
        code: response.code || 'UNKNOWN_ERROR',
        data: response.data
      });
    } else if (response && typeof response === 'object') {
      // 兼容直接返回数据的情况（如某些API没有包装成标准格式）
      if (Array.isArray(response)) {
        return response;
      } else if (response.data !== undefined) {
        return response.data;
      } else {
        return response;
      }
    } else {
      // 兼容其他格式（如果axios拦截器已经处理过）
      return response;
    }
  }).catch(error => {
    // 如果是已经格式化的错误，直接抛出
    if (error && error.success === false) {
      throw error;
    }
    
    // 处理网络错误或其他类型的错误
    if (error.response) {
      // HTTP错误响应
      const response = error.response.data;
      if (response && response.success === false) {
        throw {
          success: false,
          message: response.message || '服务器错误',
          code: response.code || error.response.status,
          data: response.data
        };
      } else {
        throw {
          success: false,
          message: response?.message || error.message || '请求失败',
          code: error.response.status || 'HTTP_ERROR'
        };
      }
    } else if (error.request) {
      // 网络错误
      throw {
        success: false,
        message: '网络连接失败，请检查网络设置',
        code: 'NETWORK_ERROR'
      };
    } else {
      // 其他错误
      throw {
        success: false,
        message: error.message || '未知错误',
        code: 'UNKNOWN_ERROR'
      };
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
    })).then(response => datasetAdapter.adaptUploadResult(response));
  },

  // 获取所有数据集
  getDatasets() {
    return handleResponse(axiosInstance.get('/api/datasets'))
      .then(response => datasetAdapter.adaptDatasetList(response));
  },

  // 获取数据集预览
  getDatasetPreview(datasetId, limit = 10) {
    return handleResponse(axiosInstance.get(`/api/datasets/${datasetId}/preview?limit=${limit}`))
      .then(response => datasetAdapter.adaptPreviewData(response));
  }
};

// 训练服务
const trainingService = {
  // 开始训练
  startTraining(trainingParams) {
    return handleResponse(axiosInstance.post('/api/train/start', trainingParams))
      .then(response => trainingAdapter.adaptStartTraining(response));
  },

  // 获取训练状态
  getTrainingStatus(jobId) {
    if (!jobId) {
      throw new Error('需要提供job_id参数');
    }
    return handleResponse(axiosInstance.get(`/api/train/status/${jobId}`))
      .then(response => trainingAdapter.adaptTrainingStatus(response));
  },

  // 停止训练
  stopTraining(jobId) {
    return handleResponse(axiosInstance.post('/api/train/stop', { job_id: jobId }));
  },

  // 获取训练日志
  getTrainingLogs(jobId, lines = 50) {
    return handleResponse(axiosInstance.get(`/api/train/logs/${jobId}?lines=${lines}`))
      .then(response => trainingAdapter.adaptTrainingLogs(response));
  },

  // 获取所有训练任务
  getTrainingJobs() {
    return handleResponse(axiosInstance.get('/api/train/jobs'))
      .then(response => trainingAdapter.adaptTrainingJobs(response));
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
    return handleResponse(axiosInstance.post('/api/predict', payload))
      .then(response => predictionAdapter.adaptPredictionResult(response));
  }
};

export {
  datasetService,
  trainingService,
  predictionService
};