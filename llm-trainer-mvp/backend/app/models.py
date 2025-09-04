# 导入必要的库和模块
from sqlmodel import SQLModel, Field  # SQLModel ORM库
from typing import Optional, List, Union, Dict, Any  # 类型提示，用于可选字段
from datetime import datetime, timedelta  # 日期时间处理
from passlib.context import CryptContext  # 密码加密
from jose import jwt  # JWT处理
from pydantic import EmailStr  # 邮箱验证
from enum import Enum  # 枚举类型
from .core.config import settings  # 应用配置

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 生成密码哈希
def get_password_hash(password):
    return pwd_context.hash(password)

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 如果没有指定令牌类型，则添加默认类型
    if "type" not in to_encode:
        to_encode.update({"type": "access"})
    # 添加过期时间和发行时间
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# 用户角色枚举
class UserRole(str, Enum):
    """用户角色枚举，定义系统中的角色类型"""
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户
    GUEST = "guest"  # 访客


# 用户模型
class User(SQLModel, table=True):
    """用户模型，存储用户信息"""
    id: Optional[int] = Field(default=None, primary_key=True)  # 主键ID，自动生成
    username: str = Field(index=True, unique=True)  # 用户名，唯一
    email: str = Field(index=True, unique=True)  # 邮箱，唯一
    hashed_password: str  # 加密后的密码
    full_name: Optional[str] = None  # 全名
    role: UserRole = Field(default=UserRole.USER)  # 用户角色，默认为普通用户
    is_active: bool = Field(default=True)  # 是否激活
    created_at: datetime = Field(default_factory=datetime.utcnow)  # 创建时间
    last_login: Optional[datetime] = None  # 最后登录时间


# 数据集模型
class Dataset(SQLModel, table=True):
    """数据集模型，存储上传的数据集信息"""
    id: Optional[int] = Field(default=None, primary_key=True)  # 主键ID，自动生成
    name: str  # 数据集名称
    file_path: str  # 数据集文件在服务器上的路径
    created_at: datetime = Field(default_factory=datetime.utcnow)  # 创建时间，默认为当前UTC时间
    total_rows: Optional[int] = None  # 数据集总行数
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")  # 关联的用户ID


# 训练任务模型
class TrainingJob(SQLModel, table=True):
    """训练任务模型，存储模型训练的配置和状态"""
    # 关闭Pydantic v2的受保护命名空间限制，允许使用 model_name 字段
    # 因为model是Pydantic的保留字，需要特殊配置才能使用model_name
    model_config = {"protected_namespaces": ()}

    id: Optional[int] = Field(default=None, primary_key=True)  # 主键ID，自动生成
    dataset_id: int = Field(foreign_key="dataset.id")  # 关联的数据集ID
    user_id: int = Field(foreign_key="user.id")  # 关联的用户ID
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
    training_job_id: int = Field(foreign_key="trainingjob.id")  # 关联的训练任务ID
    user_id: int = Field(foreign_key="user.id")  # 关联的用户ID
    name: str  # 模型名称
    file_path: str  # 模型文件在服务器上的路径
    created_at: datetime = Field(default_factory=datetime.utcnow)  # 创建时间，默认为当前UTC时间
    metrics: Optional[str] = None  # 模型评估指标，JSON格式字符串