from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


# Base properties shared across schemas
class UserBase(BaseModel):
    email: EmailStr


# Schema for User Registration (Input)
class UserCreate(UserBase):
    password: str


# Schema for User Login (Input)
class UserLogin(UserBase):
    password: str


# Schema for Token Response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schema for Token Data (Stored in JWT payload)
class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None


# Schema for Public User Data (Output)
# This prevents leaking the password_hash to the frontend
class UserPublic(UserBase):
    id: UUID
    created_at: datetime

    # Pydantic v2 configuration to allow attribute reading from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)
