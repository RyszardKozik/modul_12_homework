from pydantic import BaseModel
from typing import List, Optional

class ContactBase(BaseModel):
    name: str
    email: str
    phone: str

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: int
    contacts: List[Contact] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
