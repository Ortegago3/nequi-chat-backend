from datetime import datetime, timezone
from typing import Iterable

def contains_banned(content: str, banned_words: Iterable[str]) -> bool:
    lowered = content.lower()
    return any(w.strip().lower() in lowered for w in banned_words if w.strip())

def compute_metadata(content: str) -> tuple[int, int, str]:
    words = content.split()
    word_count = len(words)
    char_count = len(content)
    processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return word_count, char_count, processed_at