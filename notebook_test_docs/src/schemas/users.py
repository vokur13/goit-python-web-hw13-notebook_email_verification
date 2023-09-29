from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: User
    detail: str = "User successfully created"


class Token(BaseModel):
    token_type: str = "bearer"
    access_token: str
    refresh_token: str


class RequestEmail(BaseModel):
    email: EmailStr
