from sqlalchemy.orm import Session
from app.schemas.message import MessageIn, MessageOut, MessageMetadata
from app.models.message import Message
from app.repositories.message_repo import MessageRepository
from app.services.pipeline import contains_banned, compute_metadata
from app.core.config import settings
from app.errors import forbidden_content

class MessageService:
    def __init__(self, db: Session):
        self.repo = MessageRepository(db)

    def process_and_store(self, payload: MessageIn) -> MessageOut:
        # Filtro
        if contains_banned(payload.content, settings.banned_words):
            if settings.reject_on_banned:
                forbidden_content("El mensaje contiene palabras no permitidas")
            content = payload.content
            for w in settings.banned_words:
                w = w.strip()
                if w:
                    content = content.replace(w, "*" * len(w))
        else:
            content = payload.content

        wc, cc, processed = compute_metadata(content)
        m = Message(
            message_id=payload.message_id,
            session_id=payload.session_id,
            content=content,
            timestamp=payload.timestamp,
            sender=payload.sender,
            word_count=wc,
            character_count=cc,
            processed_at=processed,
        )
        saved = self.repo.create(m)
        return MessageOut(
            message_id=saved.message_id,
            session_id=saved.session_id,
            content=saved.content,
            timestamp=saved.timestamp,
            sender=saved.sender,
            metadata=MessageMetadata(
                word_count=saved.word_count,
                character_count=saved.character_count,
                processed_at=saved.processed_at,
            ),
        )