# 数据集相关API路由
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from typing import List
import pandas as pd
import os

from ..core.response import APIResponse
from ..core.errors import DatasetNotFoundException, InvalidParamsException
from ..core.logger import setup_logger
from ..core.decorators import standardized_response
from ..schemas import DatasetResponse, DatasetPreviewResponse
from ..services.dataset_service import dataset_service
from ..core.config import settings
from ..api.auth import get_current_active_user
from ..models import User

# 创建路由器
router = APIRouter(prefix="/datasets", tags=["datasets"])
logger = setup_logger(__name__)



@router.post("/upload", response_model=dict)
@standardized_response("数据集上传成功")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传数据集文件
    
    - **file**: CSV格式的数据集文件，必须包含'text'和'label'列
    - 需要用户认证
    """
    # 检查文件类型
    if not file.filename.endswith('.csv'):
        raise InvalidParamsException("只支持CSV文件格式")
    
    # 调用服务层处理上传，传入用户ID
    result = await dataset_service.upload_dataset(file, current_user.id)
    return result


@router.get("", response_model=dict)
@standardized_response("获取数据集列表成功")
async def list_datasets(current_user: User = Depends(get_current_active_user)):
    """
    获取所有数据集列表
    - 需要用户认证
    """
    datasets = await dataset_service.get_all_datasets(user_id=current_user.id)
    return datasets  # 装饰器会自动包装为标准格式


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
@standardized_response("获取数据集预览成功")
async def preview_dataset(
    dataset_id: int, 
    limit: int = Query(default=10, ge=1, le=100, description="预览行数"),
    current_user: User = Depends(get_current_active_user)
):
    """
    预览数据集内容
    
    - **dataset_id**: 数据集ID
    - **limit**: 预览行数，范围1-100
    - 需要用户认证
    """
    preview_data = await dataset_service.preview_dataset(dataset_id, limit, user_id=current_user.id)
    return preview_data


@router.delete("/{dataset_id}")
@standardized_response("数据集删除成功")
async def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除数据集
    
    - **dataset_id**: 数据集ID
    - 需要用户认证
    """
    await dataset_service.delete_dataset(dataset_id, user_id=current_user.id)
    return {"deleted": True}