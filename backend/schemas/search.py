from pydantic import BaseModel
from typing import List, Optional

class Point(BaseModel):
    lat: float
    lon: float

class SearchResultItem(BaseModel):
    name: str
    category: Optional[str] = "unknown"
    address: Optional[str] = "N/A"
    location: Point

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
