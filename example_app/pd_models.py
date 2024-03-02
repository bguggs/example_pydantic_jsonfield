from datetime import datetime

from pydantic import BaseModel, Field


class SampleProduct(BaseModel):
    name: str = Field(..., example="Example Product Name")
    description: str = Field(..., example="Example Product Description")
    price: float = Field(..., example=9.99)
    created: datetime = Field(..., default_factory=datetime.now)
    tags: list[str] = Field(default=[], example=["electronics", "gadget"])
