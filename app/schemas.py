import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class PostParams(BaseModel):
    title: str
    content: str
    published: bool = True
    contact: Optional[str] = None

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v):
        if v is None:
            return v  # or return default value
        digits_only = re.sub(r"\D", "", v)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number should be between 10-15 digits")
        return digits_only


class UpdatePostParams(PostParams):
    pass


class PostResponse(PostParams):
    created_at: datetime
    owner_id: int

    class config:
        from_attributes = True


class CreatUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    email: EmailStr
    message: str = "User created successfully"


class loginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None

    class Config:
        from_attributes = True
