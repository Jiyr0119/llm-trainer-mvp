# 数据集服务层
# 处理数据集相关的业务逻辑

import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from fastapi import UploadFile

from sqlmodel import Session, select
from ..models import Dataset
from ..db import get_session
from ..core.config import settings
from ..core.errors import DatasetNotFoundException, InvalidParamsException, InternalServerException

logger = logging.getLogger(__name__)


class DatasetService:
    """数据集服务类"""
    
    def __init__(self):
        self.upload_path = settings.UPLOAD_PATH
        os.makedirs(self.upload_path, exist_ok=True)
    
    async def upload_dataset(self, file: UploadFile) -> Dict[str, Any]:
        """
        上传数据集文件
        
        Args:
            file: 上传的文件对象
            
        Returns:
            Dict: 包含数据集信息的字典
            
        Raises:
            InvalidParamsException: 文件格式不正确
            InternalServerException: 数据集处理失败
        """
        try:
            # 验证文件格式
            if not file.filename.endswith('.csv'):
                raise InvalidParamsException("只支持CSV文件格式")
            
            # 生成唯一文件名
            timestamp = int(datetime.now().timestamp())
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(self.upload_path, filename)
            
            # 保存文件
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # 验证CSV文件格式和内容
            try:
                df = pd.read_csv(file_path)
                
                # 检查必要的列
                required_columns = ['text', 'label']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    os.remove(file_path)  # 删除无效文件
                    raise InvalidParamsException(f"数据集缺少必要的列: {missing_columns}")
                
                # 检查数据是否为空
                if len(df) == 0:
                    os.remove(file_path)
                    raise InvalidParamsException("数据集文件为空")
                
                total_rows = len(df)
                
            except pd.errors.EmptyDataError:
                os.remove(file_path)
                raise InvalidParamsException("CSV文件为空或格式错误")
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise InvalidParamsException(f"CSV文件解析失败: {str(e)}")
            
            # 保存到数据库
            try:
                with get_session() as session:
                    dataset = Dataset(
                        name=file.filename,
                        file_path=file_path,
                        created_at=datetime.utcnow(),
                        total_rows=total_rows
                    )
                    session.add(dataset)
                    session.commit()
                    session.refresh(dataset)
                    
                    result = {
                        "id": dataset.id,
                        "name": dataset.name,
                        "file_path": dataset.file_path,
                        "created_at": dataset.created_at.isoformat(),
                        "total_rows": total_rows
                    }
                    
                logger.info(f"数据集上传成功: {filename}, 共{total_rows}行数据")
                return result
                
            except Exception as e:
                # 数据库操作失败，删除文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise InternalServerException(f"保存数据集信息失败: {str(e)}")
                
        except Exception as e:
            logger.error(f"数据集上传失败: {str(e)}")
            if isinstance(e, (InvalidParamsException, InternalServerException)):
                raise
            raise InternalServerException(f"数据集上传失败: {str(e)}")
    
    async def get_all_datasets(self) -> List[Dict[str, Any]]:
        """
        获取所有数据集列表
        
        Returns:
            List[Dict]: 数据集列表
        """
        try:
            with get_session() as session:
                statement = select(Dataset).order_by(Dataset.id.desc())
                results = session.exec(statement).all()
                
                datasets = []
                for dataset in results:
                    datasets.append({
                        "id": dataset.id,
                        "name": dataset.name,
                        "file_path": dataset.file_path,
                        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
                        "total_rows": getattr(dataset, 'total_rows', None)
                    })
                
                logger.info(f"获取数据集列表成功，共{len(datasets)}个数据集")
                return datasets
                
        except Exception as e:
            logger.error(f"获取数据集列表失败: {str(e)}")
            raise InternalServerException(f"获取数据集列表失败: {str(e)}")
    
    async def preview_dataset(self, dataset_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        预览数据集内容
        
        Args:
            dataset_id: 数据集ID
            limit: 预览行数
            
        Returns:
            Dict: 包含预览数据的字典
            
        Raises:
            DatasetNotFoundException: 数据集不存在
            InternalServerException: 数据集处理失败
        """
        try:
            with get_session() as session:
                dataset = session.get(Dataset, dataset_id)
                if not dataset:
                    raise DatasetNotFoundException()
                
                # 检查文件是否存在
                if not os.path.exists(dataset.file_path):
                    raise InternalServerException(f"数据集文件不存在: {dataset.file_path}")
                
                # 读取CSV文件并预览
                try:
                    df = pd.read_csv(dataset.file_path)
                    preview_data = df.head(limit).to_dict('records')
                    
                    result = {
                        "dataset": {
                            "id": dataset.id,
                            "name": dataset.name,
                            "created_at": dataset.created_at.isoformat() if dataset.created_at else None
                        },
                        "preview": preview_data,
                        "total_rows": len(df),
                        "columns": df.columns.tolist(),
                        "preview_rows": len(preview_data)
                    }
                    
                    logger.info(f"数据集预览成功: ID={dataset_id}, 预览{len(preview_data)}行")
                    return result
                    
                except Exception as e:
                    raise InternalServerException(f"读取数据集文件失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"数据集预览失败: {str(e)}")
            if isinstance(e, (DatasetNotFoundException, InternalServerException)):
                raise
            raise InternalServerException(f"数据集预览失败: {str(e)}")
    
    async def delete_dataset(self, dataset_id: int) -> bool:
        """
        删除数据集
        
        Args:
            dataset_id: 数据集ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            DatasetNotFoundException: 数据集不存在
            InternalServerException: 删除失败
        """
        try:
            with get_session() as session:
                dataset = session.get(Dataset, dataset_id)
                if not dataset:
                    raise DatasetNotFoundException()
                
                file_path = dataset.file_path
                
                # 从数据库删除记录
                session.delete(dataset)
                session.commit()
                
                # 删除文件
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"数据集文件已删除: {file_path}")
                    except Exception as e:
                        logger.warning(f"删除数据集文件失败: {str(e)}")
                
                logger.info(f"数据集删除成功: ID={dataset_id}")
                return True
                
        except Exception as e:
            logger.error(f"删除数据集失败: {str(e)}")
            if isinstance(e, (DatasetNotFoundException, InternalServerException)):
                raise
            raise InternalServerException(f"删除数据集失败: {str(e)}")
    
    async def get_dataset_by_id(self, dataset_id: int) -> Dict[str, Any]:
        """
        根据ID获取数据集信息
        
        Args:
            dataset_id: 数据集ID
            
        Returns:
            Dict: 数据集信息
            
        Raises:
            DatasetNotFoundException: 数据集不存在
        """
        try:
            with get_session() as session:
                dataset = session.get(Dataset, dataset_id)
                if not dataset:
                    raise DatasetNotFoundException()
                
                return {
                    "id": dataset.id,
                    "name": dataset.name,
                    "file_path": dataset.file_path,
                    "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
                    "total_rows": getattr(dataset, 'total_rows', None)
                }
                
        except Exception as e:
            logger.error(f"获取数据集失败: {str(e)}")
            if isinstance(e, DatasetNotFoundException):
                raise
            raise InternalServerException(f"获取数据集失败: {str(e)}")


# 全局数据集服务实例
dataset_service = DatasetService()