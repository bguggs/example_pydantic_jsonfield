# Generated by Django 5.0.2 on 2024-03-03 04:04

import example_app.models
import example_app.pd_models
import pydantic_jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("example_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParentProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "details",
                    pydantic_jsonfield.fields.PydanticJSONField(
                        decoder=pydantic_jsonfield.fields.PydanticModelDecoder,
                        encoder=pydantic_jsonfield.fields.PydanticModelEncoder,
                        pydantic_model=example_app.pd_models.ParentProductDefinition,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="product",
            name="details",
            field=pydantic_jsonfield.fields.PydanticJSONField(
                decoder=pydantic_jsonfield.fields.PydanticModelDecoder,
                encoder=example_app.models.CustomPydanticModelEncoder,
                pydantic_model=example_app.pd_models.ProductDefinition,
            ),
        ),
    ]
