def test_websocket_broadcast_on_post_message(client, H):
    session_id = "ws-s1"
    with client.websocket_connect(f"/ws/messages/{session_id}") as ws:
        r = client.post(
            "/api/messages",
            headers=H,
            json={
                "message_id": "ws-1",
                "session_id": session_id,
                "content": "hola ws",
                "timestamp": "2023-06-15T14:30:00Z",
                "sender": "user",
            },
        )
        assert r.status_code == 201
        msg = ws.receive_json()
        assert msg["event"] == "message.created"
        data = msg["data"]
        assert data["message_id"] == "ws-1"
        assert data["session_id"] == session_id
        assert data["metadata"]["word_count"] >= 2