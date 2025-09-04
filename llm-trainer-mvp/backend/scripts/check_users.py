from app.db import get_db_context
from app.models import User
from sqlmodel import select

with get_db_context() as db:
    users = db.exec(select(User)).all()
    print([{"id": u.id, "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active} for u in users])