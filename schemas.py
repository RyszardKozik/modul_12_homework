from pydantic import BaseModel

class ContactBase(BaseModel):
    name: str
    email: str
    phone_number: str

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
