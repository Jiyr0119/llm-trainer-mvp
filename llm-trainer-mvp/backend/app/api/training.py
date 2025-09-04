# 训练相关API路由
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List
from datetime import datetime

from ..core.response import APIResponse
from ..core.errors import TrainingNotFoundException, DatasetNotFoundException
from ..core.logger import setup_logger
from ..schemas import (
    TrainingRequest, TrainingResponse, TrainingStatusResponse, 
    TrainingJobResponse, StopTrainingRequest
)
from ..services.training_service import TrainingService
from ..core.decorators import standardized_response

# 创建路由器
router = APIRouter(prefix="/train", tags=["training"])
logger = setup_logger(__name__)

# 初始化服务
training_service = TrainingService()


@router.post("/start", response_model=TrainingResponse)
async def start_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    开始模型训练
    
    - **dataset_id**: 数据集ID
    - **epochs**: 训练轮数 (1-50)
    - **learning_rate**: 学习率 (0-1)
    - **batch_size**: 批次大小 (1-128)
    - **description**: 训练描述 (可选)
    """
    job = await training_service.start_training(request)
    # 返回符合TrainingResponse模型的对象
    return TrainingResponse(
        job_id=job.id,
        status=job.status,
        message="训练任务已提交"
    )


@router.get("/status/{job_id}", response_model=TrainingStatusResponse)
async def get_training_status(job_id: int):
    """
    获取训练任务状态
    
    - **job_id**: 训练任务ID
    """
    status_data = await training_service.get_training_status(job_id)
    return status_data


@router.post("/stop")
@standardized_response("训练任务已停止")
async def stop_training(request: StopTrainingRequest):
    """
    停止训练任务
    
    - **job_id**: 训练任务ID
    """
    result = await training_service.stop_training(request.job_id)
    return result


@router.get("/jobs", response_model=List[TrainingJobResponse])

async def get_training_jobs():
    """
    获取所有训练任务列表
    """
    jobs = await training_service.get_training_jobs()
    return jobs  # 直接返回列表，而不是包装在data中


@router.get("/logs/{job_id}")
@standardized_response("获取训练日志成功")
async def get_training_logs(
    job_id: int,
    lines: int = Query(default=50, ge=1, le=1000, description="日志行数")
):
    """
    获取训练日志
    
    - **job_id**: 训练任务ID
    - **lines**: 日志行数，范围1-1000
    """
    logs = await training_service.get_training_logs(job_id, lines)
    return {"logs": logs}