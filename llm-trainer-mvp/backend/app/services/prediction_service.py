# 预测服务层
# 处理模型推理相关的业务逻辑

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from sqlmodel import Session, select

from ..models import Dataset, TrainingJob
from ..db import get_session
from ..schemas import PredictionRequest, PredictionResponse
from ..utils.exceptions import PredictionException, ResourceNotFoundException

logger = logging.getLogger(__name__)


class PredictionService:
    """预测服务类"""
    
    def __init__(self):
        self.default_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.model_cache = {}
    
    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        执行文本预测
        
        Args:
            request: 预测请求对象
            
        Returns:
            PredictionResponse: 预测结果
            
        Raises:
            ValueError: 输入参数无效
            PredictionException: 预测执行失败
        """
        try:
            logger.info(f"开始文本预测: text_length={len(request.text)}, model_id={request.model_id}")
            
            # 验证输入
            if not request.text or len(request.text.strip()) == 0:
                raise ValueError("预测文本不能为空")
            
            # 获取模型信息
            model_info = await self._get_model_info(request.model_id)
            model_name = model_info.get('model_name', self.default_model_name)
            
            # 模拟预测过程
            predicted_class, confidence = await self._simulate_prediction(request.text)
            
            logger.info(f"预测完成: class={predicted_class}, confidence={confidence:.4f}")
            
            return PredictionResponse(
                text=request.text,
                predicted_class=predicted_class,
                confidence=confidence,
                model_id=request.model_id
            )
            
        except Exception as e:
            logger.error(f"文本预测失败: {str(e)}")
            if isinstance(e, ValueError):
                raise
            raise PredictionException(f"预测失败: {str(e)}")
    
    async def _get_model_info(self, model_id: Optional[int]) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_id: 模型ID，如果为None则使用默认模型
            
        Returns:
            Dict: 模型信息字典
        """
        if model_id is None:
            logger.info("使用默认预训练模型")
            return {
                'model_id': None,
                'model_name': self.default_model_name,
                'model_type': 'pretrained'
            }
        
        # 查询训练任务中的模型
        with get_session() as session:
            training_job = session.exec(
                select(TrainingJob).where(
                    TrainingJob.id == model_id,
                    TrainingJob.status == "completed"
                )
            ).first()
            
            if training_job and training_job.model_name:
                logger.info(f"使用训练模型: {training_job.model_name}")
                return {
                    'model_id': model_id,
                    'model_name': training_job.model_name,
                    'model_type': 'trained'
                }
            
            # 如果找不到训练模型，回退到默认模型
            logger.warning(f"模型ID {model_id} 不存在或未完成训练，使用默认模型")
            return {
                'model_id': None,
                'model_name': self.default_model_name,
                'model_type': 'pretrained'
            }
    
    async def _simulate_prediction(self, text: str) -> tuple[str, float]:
        """
        模拟模型预测（实际实现中应替换为真实的模型推理）
        
        Args:
            text: 输入文本
            
        Returns:
            Tuple: (predicted_class, confidence)
        """
        # 模拟一些处理时间
        await asyncio.sleep(0.1)
        
        # 简单的模拟逻辑
        text_length = len(text)
        if text_length < 10:
            predicted_class = "简短"
            confidence = 0.85
        elif text_length < 50:
            predicted_class = "中等"
            confidence = 0.75
        else:
            predicted_class = "长文本"
            confidence = 0.92
        
        return predicted_class, confidence
    
    def clear_cache(self):
        """清理模型缓存"""
        self.model_cache.clear()
        logger.info("模型缓存已清理")


# 全局预测服务实例
prediction_service = PredictionService()