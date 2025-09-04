# 训练服务层
# 处理模型训练相关的业务逻辑

import os
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlmodel import Session, select
from ..models import TrainingJob, Dataset
from ..db import get_session
from ..core.config import settings
from ..schemas import TrainingRequest
from ..core.errors import TrainingNotFoundException, DatasetNotFoundException, InternalServerException, InvalidParamsException

logger = logging.getLogger(__name__)


class TrainingService:
    """训练服务类"""
    
    def __init__(self):
        self.log_path = settings.LOG_PATH
        self.model_path = settings.MODEL_PATH
        os.makedirs(self.log_path, exist_ok=True)
        os.makedirs(self.model_path, exist_ok=True)
    
    async def start_training(self, request: TrainingRequest, user_id: int = None) -> TrainingJob:
        """
        启动训练任务
        
        Args:
            request: 训练请求对象
            user_id: 用户ID，用于验证权限
            
        Returns:
            TrainingJob: 创建的训练任务
            
        Raises:
            ValidationException: 参数验证失败
            TrainingNotFoundException: 数据集不存在或无权访问
            InternalServerException: 训练启动失败
        """
        try:
            with get_session() as session:
                # 验证数据集是否存在
                dataset = session.get(Dataset, request.dataset_id)
                if not dataset:
                    raise DatasetNotFoundException()
                
                # 验证用户权限
                if user_id is not None and dataset.user_id != user_id:
                    raise DatasetNotFoundException("您没有权限使用此数据集")
                
                # 检查数据集文件是否存在
                if not os.path.exists(dataset.file_path):
                    raise ValidationException(f"数据集文件不存在: {dataset.file_path}")
                
                # 创建训练任务记录
                job = TrainingJob(
                    dataset_id=request.dataset_id,
                    status="pending",
                    started_at=datetime.utcnow(),
                    epochs=request.epochs,
                    learning_rate=request.learning_rate,
                    batch_size=request.batch_size,
                    progress=0.0,
                    description=request.description
                )
                
                session.add(job)
                session.commit()
                session.refresh(job)
                
                # 创建日志文件
                log_file = os.path.join(self.log_path, f"training_job_{job.id}.log")
                job.log_file = log_file
                session.add(job)
                session.commit()
                
                # 启动后台训练任务
                asyncio.create_task(self._run_training_task(job.id))
                
                logger.info(f"训练任务启动成功: ID={job.id}, dataset_id={request.dataset_id}")
                # 返回一个新的TrainingJob对象，避免会话绑定问题
                return TrainingJob(
                    id=job.id,
                    dataset_id=job.dataset_id,
                    status=job.status,
                    model_name=job.model_name,
                    epochs=job.epochs,
                    learning_rate=job.learning_rate,
                    batch_size=job.batch_size,
                    progress=job.progress,
                    log_file=job.log_file,
                    started_at=job.started_at,
                    completed_at=job.completed_at
                )
            
        except Exception as e:
            logger.error(f"启动训练任务失败: {str(e)}")
            if isinstance(e, (ValidationException, TrainingNotFoundException, InternalServerException)):
                raise
            raise InternalServerException(f"启动训练任务失败: {str(e)}")
    
    async def get_training_status(self, job_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        获取训练状态
        
        Args:
            job_id: 训练任务ID
            user_id: 用户ID，用于验证权限
            
        Returns:
            Dict: 训练状态信息
            
        Raises:
            TrainingNotFoundException: 训练任务不存在或无权访问
        """
        try:
            with get_session() as session:
                job = session.get(TrainingJob, job_id)
                if not job:
                    raise TrainingNotFoundException("训练任务", job_id)
                
                # 验证用户权限
                if user_id is not None:
                    # 获取关联的数据集
                    dataset = session.get(Dataset, job.dataset_id)
                    if dataset and dataset.user_id != user_id:
                        raise TrainingNotFoundException("您没有权限访问此训练任务")
                
                # 读取最新日志
                logs = []
                if job.log_file and os.path.exists(job.log_file):
                    try:
                        with open(job.log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            logs = [line.strip() for line in lines[-10:]]  # 最后10行
                    except Exception as e:
                        logger.warning(f"读取日志文件失败: {str(e)}")
                
                result = {
                    "job_id": job.id,
                    "dataset_id": job.dataset_id,
                    "status": job.status,
                    "progress": job.progress,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "model_name": job.model_name,
                    "epochs": job.epochs,
                    "learning_rate": job.learning_rate,
                    "batch_size": job.batch_size,
                    "logs": logs
                }
                
                return result
            
        except Exception as e:
            logger.error(f"获取训练状态失败: {str(e)}")
            if isinstance(e, TrainingNotFoundException):
                raise
            raise InternalServerException(f"获取训练状态失败: {str(e)}")
    
    async def stop_training(self, job_id: int, user_id: int = None) -> bool:
        """
        停止训练任务
        
        Args:
            job_id: 训练任务ID
            user_id: 用户ID，用于验证权限
            
        Returns:
            bool: 是否成功停止
            
        Raises:
            TrainingNotFoundException: 训练任务不存在或无权访问
            InternalServerException: 停止失败
        """
        try:
            with get_session() as session:
                job = session.get(TrainingJob, job_id)
                if not job:
                    raise TrainingNotFoundException("训练任务", job_id)
                
                # 只有pending或running状态的任务可以停止
                if job.status not in ["pending", "running"]:
                    raise InternalServerException(f"任务状态为{job.status}，无法停止")
                
                # 更新状态
                job.status = "stopped"
                job.completed_at = datetime.utcnow()
                session.add(job)
                session.commit()
                
                # 写入停止日志
                if job.log_file:
                    try:
                        with open(job.log_file, "a", encoding="utf-8") as f:
                            f.write(f"\n[{datetime.now()}] 训练任务被用户停止\n")
                    except Exception as e:
                        logger.warning(f"写入停止日志失败: {str(e)}")
                
                logger.info(f"训练任务停止成功: ID={job_id}")
                return True
            
        except Exception as e:
            logger.error(f"停止训练任务失败: {str(e)}")
            if isinstance(e, (TrainingNotFoundException, InternalServerException)):
                raise
            raise InternalServerException(f"停止训练任务失败: {str(e)}")
    
    async def get_training_logs(self, job_id: int, lines: int, user_id: int = None) -> List[str]:
        """
        获取训练日志
        
        Args:
            job_id: 训练任务ID
            lines: 返回的日志行数
            user_id: 用户ID，用于验证权限
            
        Returns:
            List[str]: 日志行列表
            
        Raises:
            TrainingNotFoundException: 训练任务不存在或无权访问
        """
        try:
            with get_session() as session:
                job = session.get(TrainingJob, job_id)
                if not job:
                    raise TrainingNotFoundException("训练任务", job_id)
                
                logs = []
                if job.log_file and os.path.exists(job.log_file):
                    try:
                        with open(job.log_file, 'r', encoding='utf-8') as f:
                            all_lines = f.readlines()
                            logs = [line.strip() for line in all_lines[-lines:]]
                    except Exception as e:
                        logger.error(f"读取日志文件失败: {str(e)}")
                        logs = [f"日志读取失败: {str(e)}"]
                else:
                    logs = ["暂无日志"]
                
                return logs
            
        except Exception as e:
            logger.error(f"获取训练日志失败: {str(e)}")
            if isinstance(e, TrainingNotFoundException):
                raise
            raise InternalServerException(f"获取训练日志失败: {str(e)}")
    
    async def get_training_jobs(
        self, 
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: int = None
    ) -> List[TrainingJob]:
        """
        获取训练任务列表
        
        Args:
            status_filter: 状态过滤
            limit: 限制数量
            offset: 偏移量
            user_id: 用户ID，用于过滤特定用户的训练任务
            
        Returns:
            List[TrainingJob]: 训练任务列表
        """
        try:
            with get_session() as session:
                statement = select(TrainingJob).order_by(TrainingJob.id.desc())
                
                if status_filter:
                    statement = statement.where(TrainingJob.status == status_filter)
                
                # 如果提供了用户ID，则过滤该用户的训练任务
                if user_id is not None:
                    # 通过数据集关联过滤用户的训练任务
                    statement = statement.join(Dataset, TrainingJob.dataset_id == Dataset.id)
                    statement = statement.where(Dataset.user_id == user_id)
                
                statement = statement.offset(offset).limit(limit)
                
                results = session.exec(statement).all()
                
                # 创建新的对象列表，避免会话关闭后的DetachedInstanceError
                jobs = []
                for job in results:
                    jobs.append(TrainingJob(
                        id=job.id,
                        dataset_id=job.dataset_id,
                        status=job.status,
                        model_name=job.model_name,
                        epochs=job.epochs,
                        learning_rate=job.learning_rate,
                        batch_size=job.batch_size,
                        progress=job.progress,
                        log_file=job.log_file,
                        started_at=job.started_at,
                        completed_at=job.completed_at
                    ))
                
                logger.info(f"获取训练任务列表成功: 共{len(jobs)}个任务")
                return jobs
            
        except Exception as e:
            logger.error(f"获取训练任务列表失败: {str(e)}")
            raise InternalServerException(f"获取训练任务列表失败: {str(e)}")
    
    async def _run_training_task(self, job_id: int):
        """
        后台训练任务（模拟实现）
        
        Args:
            job_id: 训练任务ID
        """
        try:
            # 模拟训练过程
            await asyncio.sleep(1)  # 等待1秒
            
            # 更新状态为运行中
            with get_session() as session:
                job = session.get(TrainingJob, job_id)
                if job and job.status == "pending":
                    job.status = "running"
                    session.add(job)
                    session.commit()
            
            # 模拟训练进度更新
            for progress in range(10, 101, 10):
                await asyncio.sleep(2)  # 每2秒更新一次进度
                
                with get_session() as session:
                    job = session.get(TrainingJob, job_id)
                    if job and job.status == "running":
                        job.progress = float(progress)
                        session.add(job)
                        session.commit()
                        
                        # 写入日志
                        if job.log_file:
                            with open(job.log_file, "a", encoding="utf-8") as f:
                                f.write(f"[{datetime.now()}] 训练进度: {progress}%\n")
                    elif job and job.status == "stopped":
                        logger.info(f"训练任务{job_id}被停止")
                        return
            
            # 训练完成
            with get_session() as session:
                job = session.get(TrainingJob, job_id)
                if job and job.status == "running":
                    job.status = "completed"
                    job.progress = 100.0
                    job.completed_at = datetime.utcnow()
                    job.model_name = f"model_{job.dataset_id}_{job_id}_{int(datetime.now().timestamp())}"
                    session.add(job)
                    session.commit()
                    
                    # 写入完成日志
                    if job.log_file:
                        with open(job.log_file, "a", encoding="utf-8") as f:
                            f.write(f"[{datetime.now()}] 训练完成，模型已保存: {job.model_name}\n")
            
            logger.info(f"训练任务{job_id}完成")
            
        except Exception as e:
            logger.error(f"训练任务{job_id}执行失败: {str(e)}")
            
            # 更新状态为失败
            try:
                with get_session() as session:
                    job = session.get(TrainingJob, job_id)
                    if job:
                        job.status = "failed"
                        job.completed_at = datetime.utcnow()
                        session.add(job)
                        session.commit()
                        
                        # 写入错误日志
                        if job.log_file:
                            with open(job.log_file, "a", encoding="utf-8") as f:
                                f.write(f"[{datetime.now()}] 训练失败: {str(e)}\n")
            except Exception as log_error:
                logger.error(f"写入失败日志时出错: {str(log_error)}")


# 全局训练服务实例
training_service = TrainingService()