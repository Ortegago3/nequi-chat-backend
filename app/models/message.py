from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text
from app.core.db import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(40), nullable=False)   # ISO8601
    sender: Mapped[str] = mapped_column(String(10), nullable=False)      # "user" | "system"

    # Metadatos procesados
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_at: Mapped[str] = mapped_column(String(40), nullable=False, default="")