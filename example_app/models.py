from django.db import models
from .pd_models import SampleProduct
from example_app.fields import PydanticJSONField

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    details = PydanticJSONField(pydantic_model=SampleProduct)

    def __str__(self):
        return f"{self.details.name} {self.details.price} {self.details.created}"
