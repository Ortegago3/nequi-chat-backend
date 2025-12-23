from pydantic import BaseModel, Field, field_validator
from typing import Literal, List
from datetime import datetime

SenderType = Literal["user", "system"]

class MessageIn(BaseModel):
    message_id: str = Field(..., min_length=1, max_length=64)
    session_id: str = Field(..., min_length=1, max_length=64)
    content: str = Field(..., min_length=1)
    timestamp: str
    sender: SenderType

    @field_validator("timestamp")
    @classmethod
    def validate_iso_timestamp(cls, v: str) -> str:
        # forzar ISO 8601 válido
        datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

class MessageMetadata(BaseModel):
    word_count: int
    character_count: int
    processed_at: str

class MessageOut(BaseModel):
    message_id: str
    session_id: str
    content: str
    timestamp: str
    sender: SenderType
    metadata: MessageMetadata

class MessageListOut(BaseModel):
    status: str = "success"
    data: List[MessageOut]
    limit: int
    offset: int
    total: int

class MessageCreateResponse(BaseModel):
    status: str = "success"
    data: MessageOut