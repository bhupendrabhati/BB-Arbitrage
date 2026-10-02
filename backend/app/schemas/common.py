from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class ResponseBase(BaseModel):
    success: bool = True
    message: str = ""
    data: Any = None
    error: Optional[str] = None
    timestamp: datetime = datetime.now()


class PaginatedResponse(BaseModel):
    items: list[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 50
    pages: int = 1
