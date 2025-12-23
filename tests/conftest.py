import os
import pytest
from fastapi.testclient import TestClient

os.environ["API_KEY"] = "test-key"
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"  
os.environ["DATABASE_URL"] = "sqlite:///./test_messages_test.db"
os.environ["BANNED_WORDS"] = "spam,scam,offensive,ofensivo"
os.environ["REJECT_ON_BANNED"] = "true"

from app.main import app 
from app.core.db import Base, engine  

@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    c = TestClient(app)
    yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def H():
    return {"X-API-Key": "test-key"}