import json
from json import JSONDecodeError, JSONEncoder, JSONDecoder

from django.core.exceptions import ValidationError
from django.db import models
from pydantic import BaseModel, ValidationError as PydanticValidationError

from example_app.forms import PydanticJSONFormField


class PydanticJSONFieldDescriptor:
    """ Descriptor for PydanticJSONField to ensure that the value is always a Pydantic model instance. """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self.field
        value = instance.__dict__.get(self.field.name)
        if isinstance(value, dict):
            # Convert dict to the correct python format when accessed
            value = self.field.to_python(value)
            instance.__dict__[self.field.name] = value
        return value

    def __set__(self, instance, value):
        if not isinstance(value, self.field.pydantic_model):
            # Convert value to the correct python format upon assignment
            value = self.field.to_python(value)
        instance.__dict__[self.field.name] = value

class PydanticModelEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump_json()
        return JSONEncoder.default(self, obj)


class PydanticModelDecoder(json.JSONDecoder):
    def __init__(self, *args, pydantic_model: type[BaseModel] = None, **kwargs):
        self.pydantic_model = pydantic_model
        super().__init__(*args, object_hook=self.object_hook, **kwargs)

    def object_hook(self, obj: dict):
        if self.pydantic_model:
            return self.pydantic_model(**obj)
        return obj


class PydanticJSONField(models.JSONField):
    def __init__(self, *args, pydantic_model: type[BaseModel], **kwargs):
        self.pydantic_model = pydantic_model
        kwargs['encoder'] = kwargs.get('encoder', PydanticModelEncoder)
        kwargs['decoder'] = kwargs.get('decoder', lambda: PydanticModelDecoder(pydantic_model=pydantic_model))
        super().__init__(*args, **kwargs)

    def prepare_value(self, value: BaseModel | dict | None) -> BaseModel | None:
        """ Convert the value into a Pydantic model instance. """
        if isinstance(value, BaseModel):
            # Use the Pydantic model's .model_dump_json() method to serialize it to a JSON string
            # This ensures complex types are handled correctly
            return value
        if isinstance(value, dict):
            # If the value is already a dict, serialize it using json.dumps
            # This is for compatibility with the initial form rendering which may pass a dict
            return self.pydantic_model(**value)
        return value

    def from_db_value(self, value: str | None, expression, connection):
        """ Convert the value from the database into a Pydantic model instance. """
        if value is None:
            return value
        try:
            return json.loads(value, cls=self.decoder)
        except (PydanticValidationError, json.JSONDecodeError) as e:
            raise ValidationError(str(e))

    def to_python(self, value: BaseModel | dict | str | None) -> BaseModel | None:
        """ Convert the value into a Pydantic model instance. """
        try:
            if isinstance(value, str):
                # Decode the JSON string into a dict
                return json.loads(value, cls=self.decoder)
            elif isinstance(value, dict):
                # Instantiate the Pydantic model with the dict
                return self.pydantic_model(**value)
        except (PydanticValidationError, json.JSONDecodeError) as e:
            raise ValidationError(str(e))

        return value

    def deconstruct(self) -> tuple[str, str, list, dict]:
        name, path, args, kwargs = super().deconstruct()
        # Make sure to include 'pydantic_model' in the kwargs so Django knows about it during migrations
        kwargs['pydantic_model'] = self.pydantic_model
        return name, path, args, kwargs

    def formfield(self, **kwargs) -> PydanticJSONFormField:
        # Specify the custom form field for admin and forms
        kwargs['form_class'] = PydanticJSONFormField
        return super().formfield(pydantic_model=self.pydantic_model, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs) -> None:
        """ Set the descriptor on the model field."""
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, PydanticJSONFieldDescriptor(self))
