from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from app.models import UserRole

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

# 登录相关模型
class LoginRequest(BaseModel):
    """登录请求模型，包含登录所需的信息"""
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型，包含刷新令牌所需的信息"""
    refresh_token: str