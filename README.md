# Nequi Chat Backend (FastAPI + SQLite)

API REST de mensajes con **validación**, **filtro de contenido**, **metadatos**, **persistencia**, **autenticación por API Key**, **rate limiting**, **búsqueda**, y **WebSocket** para actualizaciones en tiempo real.

[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-%E2%9D%A4-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)](https://docs.pytest.org/)

---

## Requisitos
- Python **3.10.8**
- pip
- (Opcional) Docker, Node.js (para `wscat`)

## Stack
- FastAPI, Pydantic v2
- SQLAlchemy 2.x, SQLite
- Pytest
- WebSocket (FastAPI)

---

## Instalación & ejecución (dev)

> Elige tu entorno. Asegúrate de estar en la raíz del proyecto.

### Windows — **CMD**
```bat
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt

set API_KEY=dev-key
set RATE_LIMIT_PER_MINUTE=60
set DATABASE_URL=sqlite:///./messages.db

uvicorn app.main:app --reload
```

### Windows — **PowerShell**
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:API_KEY="dev-key"
$env:RATE_LIMIT_PER_MINUTE="60"
$env:DATABASE_URL="sqlite:///./messages.db"

uvicorn app.main:app --reload
```

### macOS / Linux — **Bash**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export API_KEY=dev-key
export RATE_LIMIT_PER_MINUTE=60
export DATABASE_URL=sqlite:///./messages.db

uvicorn app.main:app --reload
```

- OpenAPI Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health

---

## Variables de entorno

| Variable                | Default                     | Descripción                                         |
|-------------------------|-----------------------------|-----------------------------------------------------|
| `API_KEY`               | `dev-key`                   | Requerida en header `X-API-Key` para `/api/*`.      |
| `RATE_LIMIT_PER_MINUTE` | `60`                        | Peticiones por minuto por **API key + ruta**.       |
| `DATABASE_URL`          | `sqlite:///./messages.db`   | URL de la base de datos (SQLite por defecto).       |
| `BANNED_WORDS`          | `spam,scam,offensive`       | Lista coma-separada de palabras prohibidas.         |
| `REJECT_ON_BANNED`      | `true`                      | `true` rechaza; `false` **censura** el contenido.   |

---

## Estructura del proyecto

<img width="278" height="1306" alt="image" src="https://github.com/user-attachments/assets/e21de639-c54b-49a1-84c2-b7298af7a3ca" />

---

## Endpoints

### POST `/api/messages`
Crea y procesa un mensaje.

**Headers**
```
X-API-Key: <tu-api-key>
Content-Type: application/json
```

**Body**
```json
{
  "message_id": "m1",
  "session_id": "s1",
  "content": "hola equipo",
  "timestamp": "2023-06-15T14:30:00Z",
  "sender": "user"
}
```

**201 OK**
```json
{
  "status": "success",
  "data": {
    "message_id": "m1",
    "session_id": "s1",
    "content": "hola equipo",
    "timestamp": "2023-06-15T14:30:00Z",
    "sender": "user",
    "metadata": {
      "word_count": 2,
      "character_count": 11,
      "processed_at": "2023-06-15T14:30:01Z"
    }
  }
}
```

**Ejemplos `curl`**

- **Windows CMD**
```bat
curl -H "X-API-Key: dev-key" -H "Content-Type: application/json" ^
 -d "{\"message_id\":\"m1\",\"session_id\":\"s1\",\"content\":\"hola equipo\",\"timestamp\":\"2023-06-15T14:30:00Z\",\"sender\":\"user\"}" ^
 http://127.0.0.1:8000/api/messages
```

- **PowerShell**
```powershell
$H = @{ "X-API-Key" = "dev-key" }
$B = @{
  message_id = "m1"
  session_id = "s1"
  content    = "hola equipo"
  timestamp  = "2023-06-15T14:30:00Z"
  sender     = "user"
} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/messages" -Headers $H -ContentType "application/json" -Body $B
```

- **Bash**
```bash
curl -H 'X-API-Key: dev-key' -H 'Content-Type: application/json'   -d '{"message_id":"m1","session_id":"s1","content":"hola equipo","timestamp":"2023-06-15T14:30:00Z","sender":"user"}'   http://127.0.0.1:8000/api/messages
```

**Errores**
- `401 UNAUTHORIZED` (falta/incorrecta API Key)
- `400 FORBIDDEN_CONTENT` (si coincide con `BANNED_WORDS` y `REJECT_ON_BANNED=true`)
- `409 DUPLICATE` (message_id ya existe)
- `422 VALIDATION_ERROR` (payload inválido)

---

### GET `/api/messages/{session_id}`
Lista por sesión, con paginación y filtro por `sender`.

**Query**
- `limit` (1..200), `offset` (>=0)
- `sender` opcional: `user` | `system`

**Ejemplo**
```bash
curl -H 'X-API-Key: dev-key'   "http://127.0.0.1:8000/api/messages/s1?limit=10&offset=0&sender=user"
```

**200 OK**
```json
{ "status": "success", "data": [ ... ], "limit": 10, "offset": 0, "total": 3 }
```

---

### GET `/api/messages/search`
Búsqueda por `content` o `message_id` + filtros.

**Ejemplo**
```bash
curl -H 'X-API-Key: dev-key'   "http://127.0.0.1:8000/api/messages/search?query=hola&limit=10&offset=0"
```

---

## WebSocket

Suscríbete a una sesión para recibir eventos al crear mensajes en esa misma `session_id`.

**URL**
```
ws://127.0.0.1:8000/ws/messages/{session_id}
```

**Probar (necesita Node.js)**
- Terminal A:
```bash
npx wscat -c ws://127.0.0.1:8000/ws/messages/s1
```
- Terminal B:
```bash
curl -H 'X-API-Key: dev-key' -H 'Content-Type: application/json'  -d '{"message_id":"m-ws","session_id":"s1","content":"hola ws","timestamp":"2023-06-15T14:30:00Z","sender":"user"}'  http://127.0.0.1:8000/api/messages
```
**Recibirás**
```json
{"event":"message.created","data":{...}}
```

---

## Rate limit

- Ventana fija **60s** por `API key + ruta`.  
- Headers: `RateLimit-Limit`, `RateLimit-Remaining`, `Retry-After`.  

**Simular 429**
1) Baja temporalmente:
   - CMD/PowerShell: `set RATE_LIMIT_PER_MINUTE=2`
   - Bash: `export RATE_LIMIT_PER_MINUTE=2`
2) Reinicia `uvicorn` y haz 3 veces la misma petición a `/api/messages/s1`.

---

## Docker (opcional)

**Build & Run**
```bash
docker build -t nequi-chat-backend .
docker run -p 8000:8000 -e API_KEY=dev-key -e RATE_LIMIT_PER_MINUTE=60 nequi-chat-backend
```

**Smoke test**
```bash
curl http://127.0.0.1:8000/health
curl -H 'X-API-Key: dev-key' "http://127.0.0.1:8000/api/messages/s1"
```

---

## Pruebas

```bash
pytest -q
# cobertura
pytest --cov=app --cov-report=term-missing
```

---

## Troubleshooting

- **401 Unauthorized**: falta/incorrecta `X-API-Key`.
- **422 JSON decode error en Windows**: usa PowerShell `Invoke-RestMethod` o escapa comillas en CMD.
- **409 DUPLICATE**: `message_id` ya existe.
- **400 FORBIDDEN_CONTENT**: contenido coincide con `BANNED_WORDS` y está en modo rechazo.
- **429 RATE_LIMITED**: espera `Retry-After` o sube `RATE_LIMIT_PER_MINUTE`.

---

