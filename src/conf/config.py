# from pydantic import EmailStr
# from pydantic_settings import BaseSettings
#
#
# class Settings(BaseSettings):
#     sqlalchemy_database_url: str
#
#     secret_key: str
#     algorithm: str
#
#     mail_username: str
#     mail_password: str
#     mail_from: EmailStr
#     mail_port: int
#     mail_server: str
#     mail_from_name: str
#
#     redis_host: str = "localhost"
#     redis_port: int = 6379
#
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#
#
# settings = Settings()
