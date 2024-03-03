from datetime import datetime

from pydantic import BaseModel, Field


class SampleProduct(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None
    created: datetime | None = None
    tags: list[str] | None = None
