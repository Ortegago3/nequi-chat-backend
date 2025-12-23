from pydantic import BaseModel

class ErrorPayload(BaseModel):
    code: str
    message: str
    details: str | None = None

class StatusError(BaseModel):
    status: str = "error"
    error: ErrorPayload

class StatusSuccess(BaseModel):
    status: str = "success"