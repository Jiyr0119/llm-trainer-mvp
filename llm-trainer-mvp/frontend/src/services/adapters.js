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
    // 由于后端响应格式已统一，直接返回数据
    return response || [];
  },

  /**
   * 适配数据集预览数据响应
   * @param {*} response - 后端响应数据
   * @returns {Array} 预览数据行
   */
  adaptPreviewData(response) {
    // 由于后端响应格式已统一，直接返回数据
    return response || [];
  },

  /**
   * 适配数据集上传响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 上传结果
   */
  adaptUploadResult(response) {
    // 由于后端响应格式已统一，直接返回数据
    return response || {};
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
    // 由于后端响应格式已统一，直接返回数据
    return response || [];
  },

  /**
   * 适配训练状态响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 训练状态信息
   */
  adaptTrainingStatus(response) {
    // 由于后端响应格式已统一，直接返回数据
    return response || {};
  },

  /**
   * 适配训练开始响应
   * @param {*} response - 后端响应数据
   * @returns {Object} 训练开始结果
   */
  adaptStartTraining(response) {
    // 由于后端响应格式已统一，直接返回数据
    return response || {};
  },

  /**
   * 适配训练日志响应
   * @param {*} response - 后端响应数据
   * @returns {Array} 日志行
   */
  adaptTrainingLogs(response) {
    // 由于后端响应格式已统一，直接返回数据
    return response || [];
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
    // 由于后端响应格式已统一，直接返回数据
    return response || {};
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
    // 由于后端响应格式已统一，直接返回数据
    return response || {};
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