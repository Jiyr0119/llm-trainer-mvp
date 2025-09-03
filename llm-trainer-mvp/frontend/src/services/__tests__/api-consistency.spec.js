// 前后端一致性测试
// 测试前端API服务与后端响应格式的一致性

import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';
import { datasetService, trainingService, predictionService } from '../api.js';
import { ERROR_CODE_MAP, getErrorMessage, getErrorType } from '../../utils/errorCodes.js';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('API一致性测试', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('响应格式一致性', () => {
    it('应该正确处理标准成功响应格式', async () => {
      const mockResponse = {
        data: {
          success: true,
          code: 200,
          message: '操作成功',
          data: [{ id: 1, name: 'test' }]
        }
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue(mockResponse),
        post: vi.fn().mockResolvedValue(mockResponse),
        delete: vi.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      const result = await datasetService.getDatasets();
      expect(Array.isArray(result)).toBe(true);
      expect(result).toEqual([{ id: 1, name: 'test' }]);
    });

    it('应该正确处理标准错误响应格式', async () => {
      const mockErrorResponse = {
        response: {
          status: 404,
          data: {
            success: false,
            code: 20001,
            message: '数据集不存在',
            data: null
          }
        }
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockRejectedValue(mockErrorResponse),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      try {
        await datasetService.getDatasets();
        expect.fail('应该抛出错误');
      } catch (error) {
        expect(error.success).toBe(false);
        expect(error.code).toBe(20001);
        expect(error.message).toBe('数据集不存在');
      }
    });

    it('应该兼容非标准响应格式', async () => {
      const mockResponse = {
        data: [{ id: 1, name: 'test' }] // 直接返回数据数组
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      const result = await datasetService.getDatasets();
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('数据适配器测试', () => {
    it('数据集列表适配器应该正确处理各种格式', async () => {
      const testCases = [
        {
          input: { success: true, data: [{ id: 1 }] },
          expected: [{ id: 1 }]
        },
        {
          input: [{ id: 2 }], // 直接数组
          expected: [{ id: 2 }]
        },
        {
          input: { datasets: [{ id: 3 }] }, // 其他格式
          expected: [{ id: 3 }]
        }
      ];

      for (const testCase of testCases) {
        mockedAxios.create.mockReturnValue({
          get: vi.fn().mockResolvedValue({ data: testCase.input }),
          interceptors: {
            request: { use: vi.fn() },
            response: { use: vi.fn() }
          }
        });

        const result = await datasetService.getDatasets();
        expect(result).toEqual(testCase.expected);
      }
    });

    it('训练状态适配器应该提供默认值', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: { job_id: 123 } // 最小数据
        }
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      const result = await trainingService.getTrainingStatus(123);
      expect(result.job_id).toBe(123);
      expect(result.status).toBeDefined();
      expect(result.progress).toBeDefined();
      expect(typeof result.progress).toBe('number');
    });
  });

  describe('错误码同步测试', () => {
    const backendErrorCodes = {
      // 通用错误
      10000: '未知错误',
      10001: '无效的参数',
      10002: '资源不存在',
      10003: '权限不足',
      10004: '请求超时',
      
      // 数据集相关错误
      20001: '数据集不存在',
      20002: '数据集格式错误',
      20003: '数据集上传失败',
      20004: '数据集解析错误',
      
      // 训练相关错误
      30001: '训练失败',
      30002: '训练任务不存在',
      30003: '训练任务已在运行',
      30004: '停止训练失败',
      
      // 模型和预测相关错误
      40001: '模型不存在',
      40002: '模型加载失败',
      40003: '预测失败',
      
      // 系统和服务错误
      50001: '数据库错误',
      50002: '文件系统错误',
      50003: '服务不可用',
      50004: '服务器内部错误'
    };

    it('前端错误码映射应该覆盖所有后端错误码', () => {
      for (const [code, message] of Object.entries(backendErrorCodes)) {
        const frontendMessage = ERROR_CODE_MAP[parseInt(code)];
        expect(frontendMessage).toBeDefined();
        expect(typeof frontendMessage).toBe('string');
        expect(frontendMessage.length).toBeGreaterThan(0);
      }
    });

    it('错误码范围应该正确分类', () => {
      // 通用错误 (10xxx)
      expect(getErrorType(10001)).toBeDefined();
      
      // 数据集错误 (20xxx)
      expect(getErrorType(20001)).toBeDefined();
      
      // 训练错误 (30xxx)
      expect(getErrorType(30001)).toBeDefined();
      
      // 预测错误 (40xxx)
      expect(getErrorType(40001)).toBeDefined();
      
      // 系统错误 (50xxx)
      expect(getErrorType(50001)).toBeDefined();
    });

    it('错误消息应该用户友好', () => {
      // 测试几个关键错误码的消息
      expect(getErrorMessage(20001)).toContain('数据集');
      expect(getErrorMessage(30002)).toContain('训练');
      expect(getErrorMessage(40001)).toContain('模型');
      expect(getErrorMessage(50001)).toContain('数据库');
    });
  });

  describe('网络错误处理', () => {
    it('应该正确处理网络连接错误', async () => {
      const networkError = {
        request: {},
        message: 'Network Error'
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockRejectedValue(networkError),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      try {
        await datasetService.getDatasets();
        expect.fail('应该抛出网络错误');
      } catch (error) {
        expect(error.success).toBe(false);
        expect(error.code).toBe('NETWORK_ERROR');
        expect(error.message).toContain('网络');
      }
    });

    it('应该正确处理HTTP状态码错误', async () => {
      const httpError = {
        response: {
          status: 500,
          data: {
            message: '服务器内部错误'
          }
        }
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockRejectedValue(httpError),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      try {
        await datasetService.getDatasets();
        expect.fail('应该抛出HTTP错误');
      } catch (error) {
        expect(error.success).toBe(false);
        expect(error.code).toBe(500);
      }
    });
  });

  describe('API服务方法完整性', () => {
    it('数据集服务应该包含所有必要方法', () => {
      expect(typeof datasetService.uploadDataset).toBe('function');
      expect(typeof datasetService.getDatasets).toBe('function');
      expect(typeof datasetService.getDatasetPreview).toBe('function');
    });

    it('训练服务应该包含所有必要方法', () => {
      expect(typeof trainingService.startTraining).toBe('function');
      expect(typeof trainingService.getTrainingStatus).toBe('function');
      expect(typeof trainingService.stopTraining).toBe('function');
      expect(typeof trainingService.getTrainingLogs).toBe('function');
      expect(typeof trainingService.getTrainingJobs).toBe('function');
    });

    it('预测服务应该包含所有必要方法', () => {
      expect(typeof predictionService.predict).toBe('function');
    });
  });

  describe('参数验证', () => {
    it('训练状态查询应该验证job_id参数', async () => {
      try {
        await trainingService.getTrainingStatus();
        expect.fail('应该抛出参数错误');
      } catch (error) {
        expect(error.message).toContain('job_id');
      }

      try {
        await trainingService.getTrainingStatus(null);
        expect.fail('应该抛出参数错误');
      } catch (error) {
        expect(error.message).toContain('job_id');
      }
    });
  });
});