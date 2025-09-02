from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Dataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TrainingJob(SQLModel, table=True):
    # 关闭Pydantic v2的受保护命名空间限制，允许使用 model_name 字段
    model_config = {"protected_namespaces": ()}

    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int
    status: str = "pending"  # pending/running/succeeded/failed/stopped
    model_name: Optional[str] = None
    epochs: int = 3
    learning_rate: float = 2e-5
    batch_size: int = 8
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ModelArtifact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int
    path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)