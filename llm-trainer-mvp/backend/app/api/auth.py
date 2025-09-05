from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from jwt.exceptions import PyJWTError

from app.db import get_session
from app.models import User, UserRole, verify_password, get_password_hash, create_access_token
from app.schemas import UserCreate, UserResponse, UserUpdate, Token, TokenData, LoginRequest, RefreshTokenRequest
from app.core.config import settings
from app.core.response import APIResponse

# 创建路由器
router = APIRouter(prefix="/auth", tags=["认证"])

# OAuth2密码Bearer，用于获取请求头中的Authorization字段
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 根据用户名获取用户
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()
    return user

# 根据邮箱获取用户
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()
    return user

# 根据ID获取用户
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    return user

# 验证用户
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# 创建刷新令牌
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # 添加令牌类型和发行时间
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 验证令牌类型
        token_type = payload.get("type")
        if token_type and token_type == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="使用刷新令牌访问API是不允许的",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        exp = payload.get("exp")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id, role=role, exp=datetime.fromtimestamp(exp) if exp else None)
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"无效的认证凭据: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
        
    # 验证用户ID是否匹配
    if user.id != token_data.user_id:
        raise credentials_exception
        
    return user

# 获取当前活跃用户
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

# 获取当前管理员用户
async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user

# 注册新用户
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_session)):
    """注册新用户"""
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册",
        )
    
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 用户登录
@router.post("/login")
def login_for_access_token(
    db: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(None),
    credentials: dict = Body(None)
):
    """用户登录（支持表单和JSON格式）
    
    可以通过两种方式登录：
    1. 表单格式：使用OAuth2PasswordRequestForm
    2. JSON格式：直接发送包含username和password的JSON数据
    """
    # 确定使用哪种登录方式
    if credentials and "username" in credentials and "password" in credentials:
        # JSON格式登录
        login_username = credentials["username"]
        login_password = credentials["password"]
    elif form_data:
        # 表单格式登录
        login_username = form_data.username
        login_password = form_data.password
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="请提供用户名和密码"
        )
    
    user = authenticate_user(db, login_username, login_password)
    if not user:
        # 使用标准错误响应格式
        return APIResponse.error(
            message="用户名或密码错误",
            code=10003,
            data=None
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    # 创建访问令牌和刷新令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "id": user.id, 
            "role": user.role,
            "type": "access",
            "iat": datetime.utcnow().timestamp()
        },
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={
            "sub": user.username, 
            "id": user.id, 
            "role": user.role,
            "jti": f"{user.id}-{datetime.utcnow().timestamp()}"
        },
    )
    
    # 使用标准成功响应格式
    return APIResponse.success(
        data={
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
        },
        message="登录成功",
        code=200
    )


# 为了向后兼容，保留/login/json路径，但重定向到统一的登录接口
@router.post("/login/json")
def login_with_json(login_data: LoginRequest, db: Session = Depends(get_session)):
    """用户登录（JSON格式）- 为了向后兼容而保留"""
    # 直接调用统一的登录接口
    return login_for_access_token(
        db=db,
        form_data=None,
        credentials={"username": login_data.username, "password": login_data.password}
    )

# OAuth2兼容的登录端点
@router.post("/token")
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    """OAuth2兼容的登录端点"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # 使用标准错误响应格式
        return APIResponse.error(
            message="用户名或密码错误",
            code=10003,
            data=None
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    # 创建访问令牌和刷新令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
    )
    
    # 使用标准成功响应格式
    return APIResponse.success(
        data={
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
        },
        message="登录成功",
        code=200
    )

# 刷新令牌
@router.post("/refresh")
def refresh_token(refresh_token_data: RefreshTokenRequest, db: Session = Depends(get_session)):
    """刷新令牌"""
    try:
        payload = jwt.decode(refresh_token_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 验证令牌类型
        token_type = payload.get("type")
        if token_type and token_type != "refresh":
            return APIResponse.error(
                message="提供的不是有效的刷新令牌",
                code=10004,
                data=None
            )
            
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        jti: str = payload.get("jti")
        
        if username is None or user_id is None:
            return APIResponse.error(
                message="无效的刷新令牌",
                code=10005,
                data=None
            )
    except PyJWTError as e:
        return APIResponse.error(
            message=f"无效的刷新令牌: {str(e)}",
            code=10006,
            data=None
        )
    
    user = get_user_by_username(db, username=username)
    if user is None:
        return APIResponse.error(
            message="用户不存在",
            code=10007,
            data=None
        )
        
    # 验证用户ID是否匹配
    if user.id != user_id:
        return APIResponse.error(
            message="用户ID不匹配",
            code=10008,
            data=None
        )
    
    # 创建新的访问令牌和刷新令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "id": user.id, 
            "role": user.role,
            "type": "access",
            "iat": datetime.utcnow().timestamp()
        },
        expires_delta=access_token_expires,
    )
    new_refresh_token = create_refresh_token(
        data={
            "sub": user.username, 
            "id": user.id, 
            "role": user.role,
            "jti": f"{user.id}-{datetime.utcnow().timestamp()}"
        },
    )
    
    # 使用标准成功响应格式
    return APIResponse.success(
        data={
            "access_token": access_token, 
            "refresh_token": new_refresh_token, 
            "token_type": "bearer"
        },
        message="令牌刷新成功",
        code=200
    )

# 获取当前用户信息
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    # 将用户对象转换为字典
    user_data = {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "id": current_user.id,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }
    return APIResponse.success(
        data=user_data,
        message="获取用户信息成功",
        code=200
    )

# 更新当前用户信息
@router.put("/me")
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_session)):
    """更新当前用户信息"""
    # 更新邮箱
    if user_update.email is not None and user_update.email != current_user.email:
        # 检查邮箱是否已存在
        db_user = get_user_by_email(db, email=user_update.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册",
            )
        current_user.email = user_update.email
    
    # 更新全名
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    # 更新密码
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    # 提交更新
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # 将用户对象转换为字典
    user_data = {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "id": current_user.id,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }
    return APIResponse.success(
        data=user_data,
        message="更新用户信息成功",
        code=200
    )