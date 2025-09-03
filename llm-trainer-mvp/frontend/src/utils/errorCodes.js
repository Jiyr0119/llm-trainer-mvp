// 错误码映射和处理工具
// 与后端的ErrorCode枚举保持同步

/**
 * 错误码映射表
 * 将后端错误码映射为用户友好的提示信息
 */
export const ERROR_CODE_MAP = {
  // 通用错误 (10xxx)
  10000: '系统出现未知错误，请稍后重试',
  10001: '请求参数有误，请检查输入内容',
  10002: '请求的资源不存在',
  10003: '您没有权限执行此操作',
  10004: '请求超时，请稍后重试',
  
  // 数据集相关错误 (20xxx)
  20001: '数据集不存在，请检查数据集ID',
  20002: '数据集格式错误，请确保CSV文件包含text和label列',
  20003: '数据集上传失败，请重试',
  20004: '数据集解析失败，请检查文件格式',
  
  // 训练相关错误 (30xxx)
  30001: '模型训练失败，请检查数据集和参数设置',
  30002: '训练任务不存在，请刷新页面后重试',
  30003: '训练任务已在运行中',
  30004: '停止训练失败，请稍后重试',
  
  // 模型和预测相关错误 (40xxx)
  40001: '模型不存在，请先完成模型训练',
  40002: '模型加载失败，请稍后重试',
  40003: '预测失败，请检查输入文本',
  
  // 系统和服务错误 (50xxx)
  50001: '数据库连接异常，请联系管理员',
  50002: '文件系统错误，请联系管理员',
  50003: '服务暂时不可用，请稍后重试',
  50004: '服务器内部错误，请联系管理员'
}

/**
 * 错误类型分类
 */
export const ERROR_TYPES = {
  RECOVERABLE: 'recoverable', // 可恢复错误（用户可以重试）
  USER_ERROR: 'user_error',   // 用户错误（需要用户修正输入）
  SYSTEM_ERROR: 'system_error' // 系统错误（需要技术支持）
}

/**
 * 错误码分类映射
 */
export const ERROR_TYPE_MAP = {
  // 通用错误
  10000: ERROR_TYPES.SYSTEM_ERROR,
  10001: ERROR_TYPES.USER_ERROR,
  10002: ERROR_TYPES.USER_ERROR,
  10003: ERROR_TYPES.USER_ERROR,
  10004: ERROR_TYPES.RECOVERABLE,
  
  // 数据集相关错误
  20001: ERROR_TYPES.USER_ERROR,
  20002: ERROR_TYPES.USER_ERROR,
  20003: ERROR_TYPES.RECOVERABLE,
  20004: ERROR_TYPES.USER_ERROR,
  
  // 训练相关错误
  30001: ERROR_TYPES.USER_ERROR,
  30002: ERROR_TYPES.RECOVERABLE,
  30003: ERROR_TYPES.USER_ERROR,
  30004: ERROR_TYPES.RECOVERABLE,
  
  // 模型和预测相关错误
  40001: ERROR_TYPES.USER_ERROR,
  40002: ERROR_TYPES.RECOVERABLE,
  40003: ERROR_TYPES.USER_ERROR,
  
  // 系统和服务错误
  50001: ERROR_TYPES.SYSTEM_ERROR,
  50002: ERROR_TYPES.SYSTEM_ERROR,
  50003: ERROR_TYPES.RECOVERABLE,
  50004: ERROR_TYPES.SYSTEM_ERROR
}

/**
 * 根据错误码获取用户友好的错误信息
 * @param {number|string} errorCode - 错误码
 * @param {string} fallbackMessage - 备用错误信息
 * @returns {string} 用户友好的错误信息
 */
export function getErrorMessage(errorCode, fallbackMessage = '操作失败，请稍后重试') {
  const code = parseInt(errorCode)
  return ERROR_CODE_MAP[code] || fallbackMessage
}

/**
 * 根据错误码获取错误类型
 * @param {number|string} errorCode - 错误码
 * @returns {string} 错误类型
 */
export function getErrorType(errorCode) {
  const code = parseInt(errorCode)
  return ERROR_TYPE_MAP[code] || ERROR_TYPES.SYSTEM_ERROR
}

/**
 * 判断错误是否可恢复（用户可以重试）
 * @param {number|string} errorCode - 错误码
 * @returns {boolean} 是否可恢复
 */
export function isRecoverableError(errorCode) {
  return getErrorType(errorCode) === ERROR_TYPES.RECOVERABLE
}

/**
 * 判断是否为用户错误（需要用户修正输入）
 * @param {number|string} errorCode - 错误码
 * @returns {boolean} 是否为用户错误
 */
export function isUserError(errorCode) {
  return getErrorType(errorCode) === ERROR_TYPES.USER_ERROR
}

/**
 * 判断是否为系统错误（需要技术支持）
 * @param {number|string} errorCode - 错误码
 * @returns {boolean} 是否为系统错误
 */
export function isSystemError(errorCode) {
  return getErrorType(errorCode) === ERROR_TYPES.SYSTEM_ERROR
}