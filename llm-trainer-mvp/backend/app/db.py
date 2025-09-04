# 导入必要的库和模块
from contextlib import contextmanager  # 用于创建上下文管理器
from typing import Iterator, Optional  # 类型提示
import logging  # 日志记录
from sqlmodel import create_engine, Session, SQLModel  # SQLModel ORM库
from sqlalchemy.pool import QueuePool  # 连接池
from sqlalchemy.exc import SQLAlchemyError  # SQL异常处理
from .core.config import settings  # 应用配置

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
# 根据数据库URL类型配置不同的连接参数
def get_engine_args():
    """根据数据库类型返回适当的引擎参数"""
    # 默认参数
    args = {"echo": settings.DEBUG}
    
    # 如果是PostgreSQL，添加连接池配置
    if settings.DATABASE_URL.startswith("postgresql"):
        args.update({
            "poolclass": QueuePool,
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_recycle": settings.DB_POOL_RECYCLE,
        })
        logger.info(f"配置PostgreSQL连接池: 大小={settings.DB_POOL_SIZE}, 最大溢出={settings.DB_MAX_OVERFLOW}")
    
    return args

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, **get_engine_args())


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
    except SQLAlchemyError as e:
        # 发生SQLAlchemy异常时回滚事务
        session.rollback()
        logger.error(f"数据库操作失败: {str(e)}")
        # 重新抛出异常，让调用者处理
        raise
    except Exception as e:
        # 发生其他异常时回滚事务
        session.rollback()
        logger.error(f"发生未预期的异常: {str(e)}")
        raise
    finally:
        # 无论如何都确保关闭会话，释放资源
        session.close()


# 创建事务管理器
@contextmanager
def transaction(session: Optional[Session] = None) -> Iterator[Session]:
    """创建一个事务上下文，可以接受现有会话或创建新会话"""
    external_session = session is not None
    session = session or Session(engine)
    
    try:
        # 开始事务
        if not external_session:
            session.begin()
        # 返回会话给调用者
        yield session
        # 如果没有异常且是内部创建的会话，提交事务
        if not external_session:
            session.commit()
    except Exception as e:
        # 发生异常时回滚事务（如果是内部创建的会话）
        if not external_session:
            session.rollback()
        logger.error(f"事务操作失败: {str(e)}")
        raise
    finally:
        # 如果是内部创建的会话，关闭它
        if not external_session:
            session.close()