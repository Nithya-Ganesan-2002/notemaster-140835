# Models for notes and users.

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """Base model for user info."""
    email: EmailStr = Field(..., description="The user's email address.")

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=6, description="User password (min 6 characters).")

# PUBLIC_INTERFACE
class UserLogin(UserBase):
    """Model for logging in."""
    password: str = Field(..., min_length=6, description="User password.")

# PUBLIC_INTERFACE
class UserRead(UserBase):
    """Model for returning user info."""
    id: int

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base note model."""
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note body text")

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    pass

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    content: Optional[str] = Field(None, description="Updated content")

# PUBLIC_INTERFACE
class NoteRead(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
