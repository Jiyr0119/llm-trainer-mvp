from contextlib import contextmanager
from typing import Iterator
from sqlmodel import create_engine, Session, SQLModel
from .core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db() -> None:
    # Import models to register tables
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()