import os
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from src.db.database import get_db
from src.db import models
from src.repository import users as repository_users
from src.schemas.users import User
from src.services.auth import auth_service

# from src.conf.config import settings

load_dotenv()


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: models.User = Depends(auth_service.get_current_user),
):
    return current_user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: models.User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file,
        public_id=f"Notebook/{current_user.id}",
        overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(f"Notebook/{current_user.id}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
