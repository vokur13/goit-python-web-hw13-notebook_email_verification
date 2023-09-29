from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader


from src.db.database import get_db
from src.db import models
from src.repository import users as repository_users
from src.schemas.users import User
from src.services.auth import auth_service

from src.conf.config import settings


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[models.User, Depends(auth_service.get_current_user)]
):
    return current_user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: models.User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file,
        public_id=f"notebook/{current_user.id}",
        overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(f"notebook/{current_user.id}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    return await repository_users.update_avatar(current_user.email, src_url, db)
