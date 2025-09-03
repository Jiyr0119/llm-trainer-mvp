// 数据格式适配器
// 用于处理后端响应数据与前端组件期望格式之间的转换

/**
 * 数据集相关的数据适配器
 */
export const datasetAdapter = {
  /**
   * 适配数据集列表响应
   * @param {*} response - 后端响应数据
   * @returns {Array} 数据集列表
   */
  adaptDatasetList(response) {
    // 处理不同的响应格式
    if (Array.isArray(response)) {
      return response;
    } else if (response?.data && Array.isArray(response.data)) {
      return response.data;
    } else if (response?.datasets && Array.isArray(response.datasets)) {
      return response.datasets;
    }
    
    // 如果都不匹配，返回空数组
    console.warn('数据集列表响应格式不符合预期:', response);
    return [];
  },

  /**
   * 适配数据集预览数据响应
   * @param {*} response - 后端响应数据
   * @returns {Array} 预览数据行
   */
  adaptPreviewData(response) {
    // 处理不同的响应格式
    if (response?.preview && Array.isArray(response.preview)) {
      return response.preview;
    } else if (response?.data?.preview && Array.isArray(response.data.preview)) {
      return response.data.preview;
    } else if (response?.rows && Array.isArray(response.rows)) {
      return response.rows;
    } else if (Array.isArray(response)) {
      return response;
    }
    
    // 如果都不匹配，返回空数组
    console.warn('数据集预览响应格式不符合预期:', response);
    return [];
  },

  /**
   * 适配数据集上传响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 上传结果
   */
  adaptUploadResult(response) {
    const defaultResult = {
      dataset_id: null,
      filename: '',
      rows_count: 0,
      columns: [],
      created_at: new Date().toISOString()
    };

    if (response?.dataset_id) {
      return { ...defaultResult, ...response };
    } else if (response?.data?.dataset_id) {
      return { ...defaultResult, ...response.data };
    } else if (response?.id) {
      // 兼容可能的id字段
      return { ...defaultResult, dataset_id: response.id, ...response };
    }

    console.warn('数据集上传响应格式不符合预期:', response);
    return defaultResult;
  }
};

/**
 * 训练相关的数据适配器
 */
export const trainingAdapter = {
  /**
   * 适配训练任务列表响应
   * @param {*} response - 后端响应数据
   * @returns {Array} 训练任务列表
   */
  adaptTrainingJobs(response) {
    if (Array.isArray(response)) {
      return response;
    } else if (response?.data && Array.isArray(response.data)) {
      return response.data;
    } else if (response?.jobs && Array.isArray(response.jobs)) {
      return response.jobs;
    }
    
    console.warn('训练任务列表响应格式不符合预期:', response);
    return [];
  },

  /**
   * 适配训练状态响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 训练状态信息
   */
  adaptTrainingStatus(response) {
    const defaultStatus = {
      job_id: null,
      status: 'unknown',
      progress: 0,
      current_epoch: 0,
      total_epochs: 0,
      loss: null,
      accuracy: null,
      created_at: null,
      updated_at: null
    };

    if (response?.job_id || response?.id) {
      return { ...defaultStatus, ...response };
    } else if (response?.data && (response.data.job_id || response.data.id)) {
      return { ...defaultStatus, ...response.data };
    }

    console.warn('训练状态响应格式不符合预期:', response);
    return defaultStatus;
  },

  /**
   * 适配训练开始响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 训练开始结果
   */
  adaptStartTraining(response) {
    const defaultResult = {
      job_id: null,
      status: 'pending',
      message: '训练任务已提交'
    };

    if (response?.job_id) {
      return { ...defaultResult, ...response };
    } else if (response?.data?.job_id) {
      return { ...defaultResult, ...response.data };
    } else if (response?.id) {
      // 兼容可能的id字段
      return { ...defaultResult, job_id: response.id, ...response };
    }

    console.warn('训练开始响应格式不符合预期:', response);
    return defaultResult;
  },

  /**
   * 适配训练日志响应
   * @param {*} response - 后端响应数据
   * @returns {Array} 日志行
   */
  adaptTrainingLogs(response) {
    if (response?.logs && Array.isArray(response.logs)) {
      return response.logs;
    } else if (response?.data?.logs && Array.isArray(response.data.logs)) {
      return response.data.logs;
    } else if (Array.isArray(response)) {
      return response;
    }

    console.warn('训练日志响应格式不符合预期:', response);
    return [];
  }
};

/**
 * 预测相关的数据适配器
 */
export const predictionAdapter = {
  /**
   * 适配预测结果响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 预测结果
   */
  adaptPredictionResult(response) {
    const defaultResult = {
      prediction: null,
      confidence: 0,
      probabilities: {},
      processing_time: 0
    };

    if (response?.prediction !== undefined) {
      return { ...defaultResult, ...response };
    } else if (response?.data?.prediction !== undefined) {
      return { ...defaultResult, ...response.data };
    } else if (response?.result !== undefined) {
      // 兼容可能的result字段
      return { 
        ...defaultResult, 
        prediction: response.result, 
        confidence: response.confidence || 0,
        ...response 
      };
    }

    console.warn('预测结果响应格式不符合预期:', response);
    return defaultResult;
  }
};

/**
 * 通用数据适配器
 */
export const commonAdapter = {
  /**
   * 适配分页数据响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 分页数据
   */
  adaptPaginatedData(response) {
    const defaultPagination = {
      items: [],
      total: 0,
      page: 1,
      size: 10,
      pages: 0
    };

    if (response?.items && Array.isArray(response.items)) {
      return { ...defaultPagination, ...response };
    } else if (response?.data?.items && Array.isArray(response.data.items)) {
      return { ...defaultPagination, ...response.data };
    } else if (Array.isArray(response)) {
      // 如果直接返回数组，包装为分页格式
      return {
        ...defaultPagination,
        items: response,
        total: response.length,
        pages: 1
      };
    }

    console.warn('分页数据响应格式不符合预期:', response);
    return defaultPagination;
  },

  /**
   * 安全获取嵌套属性值
   * @param {Object} obj - 目标对象
   * @param {string} path - 属性路径，如 'data.user.name'
   * @param {*} defaultValue - 默认值
   * @returns {*} 属性值或默认值
   */
  safeGet(obj, path, defaultValue = null) {
    try {
      return path.split('.').reduce((current, key) => current?.[key], obj) ?? defaultValue;
    } catch (error) {
      console.warn(`安全获取属性失败: ${path}`, error);
      return defaultValue;
    }
  },

  /**
   * 标准化时间格式
   * @param {string|Date} dateValue - 时间值
   * @returns {string} 格式化的时间字符串
   */
  formatDateTime(dateValue) {
    if (!dateValue) return '';
    
    try {
      const date = new Date(dateValue);
      if (isNaN(date.getTime())) {
        return dateValue.toString();
      }
      
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch (error) {
      console.warn('时间格式化失败:', dateValue, error);
      return dateValue.toString();
    }
  }
};