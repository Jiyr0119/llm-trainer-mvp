import { describe, it, expect, vi, beforeEach } from 'vitest'
import axiosInstance from '../axios'
import { datasetService, trainingService, inferenceService } from '../api'

// 模拟axios实例
vi.mock('../axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('API服务', () => {
  beforeEach(() => {
    // 每次测试前重置模拟
    vi.resetAllMocks()
  })

  describe('数据集服务', () => {
    it('上传数据集应正确调用API', async () => {
      // 模拟成功响应
      axiosInstance.post.mockResolvedValue({
        success: true,
        data: { id: '123', name: 'test-dataset.csv' }
      })

      const file = new File(['test content'], 'test-dataset.csv', { type: 'text/csv' })
      const result = await datasetService.uploadDataset(file)

      // 验证axios被正确调用
      expect(axiosInstance.post).toHaveBeenCalledWith(
        '/api/datasets/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      )

      // 验证返回结果
      expect(result).toEqual({ id: '123', name: 'test-dataset.csv' })
    })

    it('获取数据集列表应正确调用API', async () => {
      // 模拟成功响应
      axiosInstance.get.mockResolvedValue({
        success: true,
        data: [{ id: '123', name: 'dataset1' }, { id: '456', name: 'dataset2' }]
      })

      const result = await datasetService.getDatasets()

      // 验证axios被正确调用
      expect(axiosInstance.get).toHaveBeenCalledWith('/api/datasets')

      // 验证返回结果
      expect(result).toEqual([{ id: '123', name: 'dataset1' }, { id: '456', name: 'dataset2' }])
    })

    it('获取数据集预览应正确调用API', async () => {
      // 模拟成功响应
      axiosInstance.get.mockResolvedValue({
        success: true,
        data: [{ text: 'sample1' }, { text: 'sample2' }]
      })

      const result = await datasetService.getDatasetPreview('123', 5)

      // 验证axios被正确调用
      expect(axiosInstance.get).toHaveBeenCalledWith('/api/datasets/123/preview?limit=5')

      // 验证返回结果
      expect(result).toEqual([{ text: 'sample1' }, { text: 'sample2' }])
    })

    it('处理API错误响应', async () => {
      // 模拟错误响应
      axiosInstance.get.mockResolvedValue({
        success: false,
        message: '数据集不存在',
        code: 'NOT_FOUND'
      })

      // 验证错误处理
      await expect(datasetService.getDatasets()).rejects.toEqual({
        success: false,
        message: '数据集不存在',
        code: 'NOT_FOUND',
        data: undefined
      })
    })
  })

  describe('训练服务', () => {
    it('开始训练应正确调用API', async () => {
      // 模拟成功响应
      axiosInstance.post.mockResolvedValue({
        success: true,
        data: { id: 'train-123', status: 'started' }
      })

      const trainingParams = {
        datasetId: '123',
        modelName: 'gpt2',
        epochs: 3
      }

      const result = await trainingService.startTraining(trainingParams)

      // 验证axios被正确调用
      expect(axiosInstance.post).toHaveBeenCalledWith('/api/train/start', trainingParams)

      // 验证返回结果
      expect(result).toEqual({ id: 'train-123', status: 'started' })
    })
  })
})