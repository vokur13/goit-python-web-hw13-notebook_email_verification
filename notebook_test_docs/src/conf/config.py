from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlalchemy_database_url: str = (
        "postgresql+psycopg2://user:password@localhost:5432/postgres"
    )

    secret_key: str = "secret_key"
    algorithm: str = "HS256"

    mail_username: EmailStr = "example@mail.com"
    mail_password: str = "secret"
    mail_from: EmailStr = "example@mail.com"
    mail_port: int = 587
    mail_server: str = "protocol.name.domain"
    mail_from_name: str = "Sender_Name"

    redis_host: str = "localhost"
    redis_port: int = 6379

    cloudinary_name: str = "cloudinary_name"
    cloudinary_api_key: int = "cloudinary_api_key"
    cloudinary_api_secret: str = "cloudinary_secret"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="allow",
    )


settings = Settings()
