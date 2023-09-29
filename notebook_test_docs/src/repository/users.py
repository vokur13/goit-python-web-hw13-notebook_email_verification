from libgravatar import Gravatar
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.db import models
from src.schemas.users import UserCreate


async def get_user_by_email(email: EmailStr, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


async def create_user(body: UserCreate, db: Session) -> models.User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = models.User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_token(user: models.User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def update_avatar(email, url: str, db: Session) -> models.User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
