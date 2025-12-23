from fastapi import HTTPException, status

def invalid_format(details: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": "INVALID_FORMAT", "message": "Formato de mensaje inválido", "details": details},
    )

def validation_error(details: str):
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={"code": "VALIDATION_ERROR", "message": "Error de validación", "details": details},
    )

def forbidden_content(details: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": "FORBIDDEN_CONTENT", "message": "Contenido no permitido", "details": details},
    )

def server_error(details: str):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "SERVER_ERROR", "message": "Error del servidor", "details": details},
    )