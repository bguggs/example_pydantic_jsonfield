from django.db import models
from .pd_models import ProductDefinition, ParentProductDefinition
from pydantic_jsonfield.fields import PydanticJSONField, PydanticModelEncoder


class CustomPydanticModelEncoder(PydanticModelEncoder):
    default_model_dump_json_options = {
        "indent": 2,
        "exclude_none": True,
    }


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    details = PydanticJSONField(pydantic_model=ProductDefinition, encoder=CustomPydanticModelEncoder)

    def __str__(self):
        return f"{self.details.name} {self.details.price} {self.details.created}"


class ParentProduct(models.Model):
    details = PydanticJSONField(pydantic_model=ParentProductDefinition)

    def __str__(self):
        return f"{self.details.name} {self.details.price} {self.details.created}"
