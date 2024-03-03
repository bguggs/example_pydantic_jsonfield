from datetime import datetime

from pydantic import BaseModel, Field


class ProductDefinition(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None
    created: datetime | None = None
    tags: list[str] | None = None


class ParentProductDefinition(BaseModel):
    name: str
    children: list[ProductDefinition] | None = None
