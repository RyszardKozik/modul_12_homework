from pydantic import BaseModel

class ContactBase(BaseModel):
    name: str
    email: str
    phone_number: str

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserLogin(BaseModel):
    email: str
    password: str
