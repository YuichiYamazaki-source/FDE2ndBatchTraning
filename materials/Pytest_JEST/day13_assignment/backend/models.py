from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    password: str

class UserRegister(UserBase):
    email: str
    role: str

class UserLogin(UserBase):
    pass

class UserProfile(UserBase):
    role: str
