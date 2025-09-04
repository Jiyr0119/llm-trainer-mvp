# 请求和响应数据模型定义
# 使用Pydantic模型进行数据验证和序列化

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from app.models import UserRole, User

# 用户认证相关模型
class Token(BaseModel):
    """令牌模型，用于返回JWT令牌"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据模型，用于存储JWT令牌中的数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None  # 令牌类型：access 或 refresh
    iat: Optional[datetime] = None  # 令牌发行时间
    jti: Optional[str] = None  # JWT ID，用于刷新令牌

# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型，包含用户的基本信息"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """用户创建模型，包含创建用户所需的信息"""
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度必须至少为8个字符')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        return v

class UserUpdate(BaseModel):
    """用户更新模型，包含可更新的用户信息"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('密码长度必须至少为8个字符')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        return v

class UserInDB(UserBase):
    """数据库中的用户模型，包含用户在数据库中的信息"""
    id: int
    hashed_password: str
    created_at: datetime
    last_login: Optional[datetime] = None

class UserResponse(UserBase):
    """用户响应模型，用于返回用户信息"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


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