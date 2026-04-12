from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BookmarkRequest(BaseModel):
    url: str

class BookmarkResponse(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    created_at: datetime

class BookmarksListResponse(BaseModel):
    count: int
    bookmarks: list[BookmarkResponse]

class SearchRequest(BaseModel):
    query: str