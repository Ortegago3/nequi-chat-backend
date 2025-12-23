def _post(client, H, msg_id: str, session: str, content: str, sender: str = "user"):
    return client.post(
        "/api/messages",
        headers=H,
        json={
            "message_id": msg_id,
            "session_id": session,
            "content": content,
            "timestamp": "2023-06-15T14:30:00Z",
            "sender": sender,
        },
    )

def test_search_by_content_and_message_id_and_filters(client, H):
    # Datos
    _post(client, H, "m-hello", "s-a", "hola mundo")
    _post(client, H, "m-bye", "s-a", "adios mundo", sender="system")
    _post(client, H, "m-hello-2", "s-b", "hola equipo")

    # 1) query por contenido
    r = client.get("/api/messages/search", params={"query": "hola", "limit": 10, "offset": 0}, headers=H)
    assert r.status_code == 200
    js = r.json()
    assert js["status"] == "success"
    assert js["total"] >= 2
    assert all("hola" in i["content"] for i in js["data"])

    # 2) query por message_id
    r = client.get("/api/messages/search", params={"query": "m-bye"}, headers=H)
    assert r.status_code == 200
    js = r.json()
    assert any(i["message_id"] == "m-bye" for i in js["data"])

    # 3) filtro por session_id
    r = client.get("/api/messages/search", params={"query": "m", "session_id": "s-a"}, headers=H)
    assert r.status_code == 200
    assert all(i["session_id"] == "s-a" for i in r.json()["data"])

    # 4) filtro por sender
    r = client.get("/api/messages/search", params={"query": "m", "sender": "system"}, headers=H)
    assert r.status_code == 200
    assert all(i["sender"] == "system" for i in r.json()["data"])