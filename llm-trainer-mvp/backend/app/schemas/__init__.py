# 请求和响应数据模型定义
# 使用Pydantic模型进行数据验证和序列化

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class TrainingRequest(BaseModel):
    """训练请求模型"""
    dataset_id: int = Field(..., description="数据集ID", gt=0)
    epochs: int = Field(default=3, description="训练轮数", ge=1, le=50)
    learning_rate: float = Field(default=2e-5, description="学习率", gt=0, le=1)
    batch_size: int = Field(default=8, description="批次大小", ge=1, le=128)
    description: Optional[str] = Field(None, description="训练描述", max_length=500)
    
    @validator('learning_rate')
    def validate_learning_rate(cls, v):
        if v <= 0 or v > 1:
            raise ValueError('学习率必须在0到1之间')
        return v


class TrainingResponse(BaseModel):
    """训练响应模型"""
    job_id: int = Field(..., description="训练任务ID")
    status: str = Field(..., description="训练状态")
    message: str = Field(..., description="响应消息")


class TrainingStatusResponse(BaseModel):
    """训练状态响应模型"""
    job_id: int = Field(..., description="训练任务ID")
    dataset_id: int = Field(..., description="数据集ID")
    status: str = Field(..., description="训练状态")
    progress: float = Field(default=0.0, description="训练进度", ge=0, le=100)
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    model_name: Optional[str] = Field(None, description="模型名称")
    logs: Optional[List[str]] = Field(None, description="训练日志")


class TrainingJobResponse(BaseModel):
    """训练任务列表响应模型"""
    id: int = Field(..., description="任务ID")
    dataset_id: int = Field(..., description="数据集ID")
    status: str = Field(..., description="状态")
    progress: float = Field(default=0.0, description="进度")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    model_name: Optional[str] = Field(None, description="模型名称")
    epochs: int = Field(..., description="训练轮数")
    learning_rate: float = Field(..., description="学习率")
    batch_size: int = Field(..., description="批次大小")


class StopTrainingRequest(BaseModel):
    """停止训练请求模型"""
    job_id: int = Field(..., description="训练任务ID", gt=0)


class PredictionRequest(BaseModel):
    """预测请求模型"""
    text: str = Field(..., description="待预测文本", min_length=1, max_length=10000)
    model_id: Optional[int] = Field(None, description="模型ID")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('文本内容不能为空')
        return v.strip()


class PredictionResponse(BaseModel):
    """预测响应模型"""
    text: str = Field(..., description="输入文本")
    predicted_class: str = Field(..., description="预测类别")
    confidence: float = Field(..., description="置信度", ge=0, le=1)
    model_id: Optional[int] = Field(None, description="使用的模型ID")


class DatasetResponse(BaseModel):
    """数据集响应模型"""
    id: int = Field(..., description="数据集ID")
    name: str = Field(..., description="数据集名称")
    file_path: str = Field(..., description="文件路径")
    created_at: datetime = Field(..., description="创建时间")
    total_rows: Optional[int] = Field(None, description="总行数")


class DatasetPreviewResponse(BaseModel):
    """数据集预览响应模型"""
    dataset: dict = Field(..., description="数据集信息")
    preview: List[dict] = Field(..., description="预览数据")
    total_rows: int = Field(..., description="总行数")
    columns: List[str] = Field(..., description="列名")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(default="healthy", description="服务状态")
    message: str = Field(default="LLM Trainer MVP API", description="服务信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="检查时间")
    version: str = Field(default="1.0.0", description="API版本")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="操作是否成功")
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    data: Optional[Any] = Field(None, description="附加数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="错误时间")