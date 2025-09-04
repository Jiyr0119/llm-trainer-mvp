from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import User, UserRole
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.api.auth import get_current_admin_user, get_user_by_username, get_user_by_email, get_password_hash

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])

# 获取所有用户（仅管理员）
@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """获取所有用户（仅管理员）"""
    statement = select(User).offset(skip).limit(limit)
    users = db.exec(statement).all()
    return users

# 根据ID获取用户（仅管理员）
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """根据ID获取用户（仅管理员）"""
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

# 创建用户（仅管理员）
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """创建用户（仅管理员）"""
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

# 更新用户（仅管理员）
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """更新用户（仅管理员）"""
    # 获取用户
    statement = select(User).where(User.id == user_id)
    db_user = db.exec(statement).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新邮箱
    if user_update.email is not None and user_update.email != db_user.email:
        # 检查邮箱是否已存在
        email_user = get_user_by_email(db, email=user_update.email)
        if email_user and email_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册",
            )
        db_user.email = user_update.email
    
    # 更新全名
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    
    # 更新密码
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    # 更新激活状态
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    
    # 更新角色
    if user_update.role is not None:
        db_user.role = user_update.role
    
    # 提交更新
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 删除用户（仅管理员）
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """删除用户（仅管理员）"""
    # 获取用户
    statement = select(User).where(User.id == user_id)
    db_user = db.exec(statement).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许删除自己
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的用户",
        )
    
    # 删除用户
    db.delete(db_user)
    db.commit()
    return None