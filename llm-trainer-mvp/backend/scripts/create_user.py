from app.db import get_db_context
from app.models import User, UserRole, get_password_hash
from datetime import datetime
from sqlmodel import select

def create_test_user():
    with get_db_context() as db:
        # 检查admin用户的密码哈希
        statement = select(User).where(User.username == 'admin')
        admin = db.exec(statement).first()
        if admin:
            print(f"Admin user exists: {admin.username}, hash: {admin.hashed_password}")
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Created test user: {test_user.username}, id: {test_user.id}")

if __name__ == "__main__":
    create_test_user()