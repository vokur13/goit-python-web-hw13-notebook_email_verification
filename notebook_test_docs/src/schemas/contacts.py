from datetime import date

from pydantic import BaseModel, EmailStr

from src.schemas.users import User


class ContactBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    birth_date: date
    bio: str


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int
    owner: User

    class Config:
        from_attributes = True
