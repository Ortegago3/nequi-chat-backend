from fastapi import APIRouter, Depends, Query, BackgroundTasks
from typing import Optional, List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import verify_api_key
from app.schemas.message import MessageIn, MessageCreateResponse, MessageListOut, MessageOut
from app.services.message_service import MessageService
from app.repositories.message_repo import MessageRepository
from app.api.ws import manager

router = APIRouter(prefix="/api", dependencies=[Depends(verify_api_key)])

@router.post("/messages", response_model=MessageCreateResponse, status_code=201)
def create_message(
    payload: MessageIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    out = MessageService(db).process_and_store(payload)
    background_tasks.add_task(
        manager.broadcast,
        payload.session_id,
        {"event": "message.created", "data": out.model_dump()},
    )
    return {"status": "success", "data": out}

@router.get("/messages/{session_id}", response_model=MessageListOut)
def list_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sender: Optional[str] = Query(None, pattern="^(user|system)$"),
    db: Session = Depends(get_db),
):
    repo = MessageRepository(db)
    items, total = repo.list_by_session(session_id, sender, limit, offset)
    data: List[MessageOut] = [
        MessageOut(
            message_id=i.message_id,
            session_id=i.session_id,
            content=i.content,
            timestamp=i.timestamp,
            sender=i.sender,
            metadata={"word_count": i.word_count, "character_count": i.character_count, "processed_at": i.processed_at},
        )
        for i in items
    ]
    return {"status": "success", "data": data, "limit": limit, "offset": offset, "total": total}

@router.get("/messages/search", response_model=MessageListOut)
def search_messages(
    query: str = Query(..., min_length=1),
    session_id: Optional[str] = Query(None),
    sender: Optional[str] = Query(None, pattern="^(user|system)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    repo = MessageRepository(db)
    rows, total = repo.search(query=query, session_id=session_id, sender=sender, limit=limit, offset=offset)
    data: List[MessageOut] = [
        MessageOut(
            message_id=i.message_id,
            session_id=i.session_id,
            content=i.content,
            timestamp=i.timestamp,
            sender=i.sender,
            metadata={"word_count": i.word_count, "character_count": i.character_count, "processed_at": i.processed_at},
        )
        for i in rows
    ]
    return {"status": "success", "data": data, "limit": limit, "offset": offset, "total": total}