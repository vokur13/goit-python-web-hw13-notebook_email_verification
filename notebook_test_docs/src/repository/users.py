from libgravatar import Gravatar
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.db import models
from src.schemas.users import UserCreate


async def get_user_by_email(email: EmailStr, db: Session) -> models.User:
    """
    The get_user_by_email function takes in an email address and a database session,
    and returns the user associated with that email address. If no such user exists,
    it will return None.

    :param email: EmailStr: Validate the email address
    :param db: Session: Pass the database session to the function
    :return: A user object if the email is found in the database
    :doc-author: Trelent"""
    return db.query(models.User).filter(models.User.email == email).first()


async def create_user(body: UserCreate, db: Session) -> models.User:
    """
    The create_user function creates a new user in the database.

    :param body: UserCreate: Pass the request body to the function
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent"""
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
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: Nothing
    :doc-author: Trelent"""
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_token(user: models.User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user in the database.

    :param user: models.User: Specify the user that is being updated
    :param token: str | None: Pass in the token that is returned from the spotify api
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent"""
    user.refresh_token = token
    db.commit()


async def update_avatar(email, url: str, db: Session) -> models.User:
    """
    The update_avatar function updates the avatar of a user in the database.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is being passed into the function
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: Trelent"""
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
