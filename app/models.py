from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class LinkCreate(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = Field(None, min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")

class LinkUpdate(BaseModel):
    url: HttpUrl

class LinkResponse(BaseModel):
    short_url: str
    original_url: str
    short_code: str
