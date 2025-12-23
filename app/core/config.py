import os
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Nequi Chat Backend"
    env: str = os.getenv("ENV", "dev")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./messages.db")

    # Autenticación 
    api_key: str = os.getenv("API_KEY", "dev-key")

    # Rate limit
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Filtro de contenido
    banned_words: List[str] = (
        os.getenv("BANNED_WORDS", "spam,scam,offensive").split(",")
        if os.getenv("BANNED_WORDS") else ["spam", "scam", "offensive"]
    )
    reject_on_banned: bool = os.getenv("REJECT_ON_BANNED", "true").lower() == "true"

settings = Settings()