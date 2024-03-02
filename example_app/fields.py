import json
from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.db import models
from pydantic import BaseModel, ValidationError as PydanticValidationError

from example_app.forms import PydanticJSONFormField


class PydanticFieldDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self.field
        value = instance.__dict__.get(self.field.name)
        if isinstance(value, dict):
            # Convert dict to Pydantic model instance when accessed
            value = self.field.to_python(value)
            instance.__dict__[self.field.name] = value
        return value

    def __set__(self, instance, value):
        if not isinstance(value, self.field.pydantic_model):
            # Convert value to Pydantic model instance upon assignment
            value = self.field.to_python(value)
        instance.__dict__[self.field.name] = value


class PydanticJSONField(models.JSONField):
    def __init__(self, *args, pydantic_model: type[BaseModel], **kwargs):
        self.pydantic_model = pydantic_model
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: BaseModel | str | None) -> str:
        """ Convert the value into a JSON-serializable python object before passing it to the JSONField get_prep_value method. """
        model_value: BaseModel | None = None
        try:
            if isinstance(value, dict):
                model_value = self.pydantic_model(**value)
            elif isinstance(value, str):
                model_value = self.pydantic_model(**json.loads(value))
        except (PydanticValidationError, TypeError, ValueError) as e:
            # Handle both Pydantic validation errors and potential issues
            # in the serialization/deserialization process.
            raise ValidationError(e.errors() if hasattr(e, 'errors') else str(e))

        if isinstance(value, BaseModel):
            model_value = value

        if model_value is not None:
            value = model_value.model_dump_json()

        return super().get_prep_value(value)

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

    def from_db_value(self, value: str | None, expression, connection) -> BaseModel | None:
        """ Convert the value into a Pydantic model instance. """
        if value is not None:
            try:
                return self.pydantic_model(**json.loads(value))
            except (PydanticValidationError, JSONDecodeError) as e:
                raise ValidationError(e.errors() if hasattr(e, 'errors') else str(e))
        return value

    def to_python(self, value: BaseModel | dict | str | None) -> BaseModel | None:
        """ Convert the value into a Pydantic model instance. """
        if isinstance(value, self.pydantic_model):
            return value
        try:
            if isinstance(value, dict):
                return self.pydantic_model(**value)
            if isinstance(value, str):
                return self.pydantic_model(**json.loads(value))
        except (PydanticValidationError, JSONDecodeError) as e:
            raise ValidationError(e.errors() if hasattr(e, 'errors') else str(e))
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Make sure to include 'pydantic_model' in the kwargs so Django knows about it during migrations
        kwargs['pydantic_model'] = self.pydantic_model
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # Specify the custom form field for admin and forms
        kwargs['form_class'] = PydanticJSONFormField
        return super().formfield(pydantic_model=self.pydantic_model, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, PydanticFieldDescriptor(self))
