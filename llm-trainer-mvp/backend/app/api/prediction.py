# 预测相关API路由
from fastapi import APIRouter

from ..core.logger import setup_logger
from ..core.decorators import standardized_response
from ..schemas import PredictionRequest, PredictionResponse
from ..services.prediction_service import prediction_service

# 创建路由器
router = APIRouter(prefix="/predict", tags=["prediction"])
logger = setup_logger(__name__)



@router.post("/", response_model=dict)
@standardized_response("预测成功")
async def predict(request: PredictionRequest):
    """
    执行文本分类预测
    
    - **text**: 待预测的文本内容
    - **model_id**: 使用的模型ID (可选，默认使用预训练模型)
    """
    result = await prediction_service.predict(request)
    return result  # 装饰器会自动包装为标准格式