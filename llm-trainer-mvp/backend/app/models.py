# 导入必要的库和模块
from sqlmodel import SQLModel, Field  # SQLModel ORM库
from typing import Optional  # 类型提示，用于可选字段
from datetime import datetime  # 日期时间处理


# 数据集模型
class Dataset(SQLModel, table=True):
    """数据集模型，存储上传的数据集信息"""
    id: Optional[int] = Field(default=None, primary_key=True)  # 主键ID，自动生成
    name: str  # 数据集名称
    file_path: str  # 数据集文件在服务器上的路径
    created_at: datetime = Field(default_factory=datetime.utcnow)  # 创建时间，默认为当前UTC时间


# 训练任务模型
class TrainingJob(SQLModel, table=True):
    """训练任务模型，存储模型训练的配置和状态"""
    # 关闭Pydantic v2的受保护命名空间限制，允许使用 model_name 字段
    # 因为model是Pydantic的保留字，需要特殊配置才能使用model_name
    model_config = {"protected_namespaces": ()}

    id: Optional[int] = Field(default=None, primary_key=True)  # 主键ID，自动生成
    dataset_id: int  # 关联的数据集ID
    status: str = "pending"  # 任务状态：pending(等待中)/running(运行中)/succeeded(成功)/failed(失败)/stopped(已停止)
    model_name: Optional[str] = None  # 训练后的模型名称
    epochs: int = 3  # 训练轮数，默认3轮
    learning_rate: float = 2e-5  # 学习率，默认2e-5
    batch_size: int = 8  # 批次大小，默认8
    progress: float = 0.0  # 训练进度，范围0-100
    log_file: Optional[str] = None  # 训练日志文件路径
    started_at: Optional[datetime] = None  # 训练开始时间
    completed_at: Optional[datetime] = None  # 训练完成时间


# 模型文件模型
class ModelArtifact(SQLModel, table=True):
    """模型文件模型，存储训练后的模型文件信息"""
    id: Optional[int] = Field(default=None, primary_key=True)  # 主键ID，自动生成
    job_id: int  # 关联的训练任务ID
    path: str  # 模型文件在服务器上的路径
    created_at: datetime = Field(default_factory=datetime.utcnow)  # 创建时间，默认为当前UTC时间