from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.emtity.models import Users
from src.schemas.users import UserSchema


def get_user_by_email(email: str, db: Session = Depends(get_db)):
    stmt = select(Users).filter_by(email=email)
    user = db.execute(stmt).scalar_one_or_none()
    return user


def create_user(body: UserSchema, db: Session = Depends(get_db)):
    new_user = Users(**body.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: Users, token: str | None, db: Session):
    user.refresh_token = token
    db.commit()
