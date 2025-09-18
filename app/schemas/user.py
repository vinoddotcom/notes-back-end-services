from datetime import datetime
from typing import Optional, List, Generic, TypeVar

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = "user"  # Default role is "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRole(BaseModel):
    role: str = Field(..., description="User role - 'admin' or 'user'")


class UserUpdateStatus(BaseModel):
    is_active: bool = Field(..., description="User account status")


class NoteInfo(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    updated_at: datetime
    notes: List[NoteInfo] = []

    model_config = ConfigDict(from_attributes=True)


# Pagination schemas
class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response with items and pagination metadata"""
    items: List[T] = Field(..., description="List of items in the current page")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    
    model_config = ConfigDict(from_attributes=True)


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str  # User ID
    exp: int  # Expiration time
    role: str  # User role