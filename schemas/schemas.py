from pydantic import BaseModel


class CityInfo(BaseModel):
    name: str
    count: int


class SearchHistory(BaseModel):
    city: str
    time: str
