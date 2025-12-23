from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy import or_
from app.models.message import Message

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, m: Message) -> Message:
        exists = self.db.scalar(select(func.count()).select_from(Message).where(Message.message_id == m.message_id))
        if exists:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "DUPLICATE", "message": "message_id ya existe", "details": m.message_id},
            )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return m

    def list_by_session(
        self, session_id: str, sender: Optional[str], limit: int, offset: int
    ) -> tuple[Sequence[Message], int]:
        stmt = select(Message).where(Message.session_id == session_id)
        if sender:
            stmt = stmt.where(Message.sender == sender)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = self.db.execute(stmt.order_by(Message.id).limit(limit).offset(offset)).scalars().all()
        return items, total

    def search(
        self,
        query: str,
        session_id: Optional[str],
        sender: Optional[str],
        limit: int,
        offset: int,
    ) -> tuple[Sequence[Message], int]:
        like = f"%{query}%"
        stmt = select(Message).where(or_(Message.content.ilike(like), Message.message_id.ilike(like)))
        if session_id:
            stmt = stmt.where(Message.session_id == session_id)
        if sender:
            stmt = stmt.where(Message.sender == sender)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.db.execute(stmt.order_by(Message.id).limit(limit).offset(offset)).scalars().all()
        return rows, total