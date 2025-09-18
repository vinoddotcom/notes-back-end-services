from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the note")
    description: Optional[str] = Field(None, description="Content of the note")


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    title: Optional[str] = Field(None, min_length=1, max_length=200)


class NoteResponse(NoteBase):
    id: int = Field(..., description="Unique note identifier")
    owner_id: int = Field(..., description="ID of the user who owns this note")
    created_at: datetime = Field(..., description="When the note was created")
    updated_at: datetime = Field(..., description="When the note was last updated")

    model_config = ConfigDict(from_attributes=True)