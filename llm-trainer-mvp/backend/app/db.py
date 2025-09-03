# 导入必要的库和模块
from contextlib import contextmanager  # 用于创建上下文管理器
from typing import Iterator  # 类型提示
from sqlmodel import create_engine, Session, SQLModel  # SQLModel ORM库
from .core.config import settings  # 应用配置

# 创建数据库引擎
# settings.DATABASE_URL: 数据库连接URL
# echo=False: 不输出SQL语句到控制台（生产环境推荐）
engine = create_engine(settings.DATABASE_URL, echo=False)


# 初始化数据库函数
def init_db() -> None:
    # 导入模型以注册数据库表
    # 这里导入models模块是为了确保SQLModel能够找到所有定义的模型类
    from . import models  # noqa: F401 (忽略未使用导入的警告)
    # 创建所有在SQLModel中定义的表
    SQLModel.metadata.create_all(engine)


# 创建数据库会话的上下文管理器
# 使用contextmanager装饰器简化上下文管理
@contextmanager
def get_session() -> Iterator[Session]:
    # 创建新的数据库会话
    session = Session(engine)
    try:
        # 返回会话给调用者
        yield session
        # 如果没有异常，提交事务
        session.commit()
    except Exception:
        # 发生异常时回滚事务
        session.rollback()
        # 重新抛出异常，让调用者处理
        raise
    finally:
        # 无论如何都确保关闭会话，释放资源
        session.close()