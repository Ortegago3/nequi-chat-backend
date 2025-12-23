import pytest

def test_post_message_success(client, H):
    payload = {
        "message_id": "msg-1",
        "session_id": "s-1",
        "content": "Hola, ¿cómo puedo ayudarte hoy?",
        "timestamp": "2023-06-15T14:30:00Z",
        "sender": "system",
    }
    r = client.post("/api/messages", json=payload, headers=H)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "success"
    assert body["data"]["message_id"] == "msg-1"
    assert body["data"]["metadata"]["word_count"] >= 5

def test_post_message_duplicate_id_conflict(client, H):
    payload = {
        "message_id": "msg-dup",
        "session_id": "s-dup",
        "content": "mensaje",
        "timestamp": "2023-06-15T14:30:00Z",
        "sender": "user",
    }
    r1 = client.post("/api/messages", json=payload, headers=H)
    r2 = client.post("/api/messages", json=payload, headers=H)
    assert r1.status_code == 201
    assert r2.status_code == 409
    body = r2.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "DUPLICATE"

def test_post_message_forbidden_content(client, H):
    payload = {
        "message_id": "msg-2",
        "session_id": "s-1",
        "content": "contenido ofensivo aquí",
        "timestamp": "2023-06-15T14:31:00Z",
        "sender": "user",
    }
    r = client.post("/api/messages", json=payload, headers=H)
    assert r.status_code == 400
    body = r.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "FORBIDDEN_CONTENT"

def test_post_message_invalid_sender(client, H):
    payload = {
        "message_id": "msg-3",
        "session_id": "s-1",
        "content": "hola",
        "timestamp": "2023-06-15T14:32:00Z",
        "sender": "robot",
    }
    r = client.post("/api/messages", json=payload, headers=H)
    assert r.status_code in (400, 422)

def test_get_messages_pagination_and_filter(client, H):
    for i in range(10):
        client.post(
            "/api/messages",
            json={
                "message_id": f"msg-batch-{i}",
                "session_id": "s-2",
                "content": f"mensaje {i}",
                "timestamp": f"2023-06-15T14:{30+i:02d}:00Z",
                "sender": "user" if i % 2 == 0 else "system",
            },
            headers=H,
        )
    r = client.get("/api/messages/s-2", params={"limit": 3, "offset": 2, "sender": "user"}, headers=H)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["limit"] == 3
    assert data["offset"] == 2
    assert "total" in data
    assert all(item["sender"] == "user" for item in data["data"])
