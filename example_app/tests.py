from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Product
from .pd_models import ProductDefinition


class ProductModelTest(TestCase):
    def setUp(self):
        self.valid_product_details = {
            "name": "Smart Watch",
            "description": "A smart watch with health tracking features.",
            "created": "2021-01-01T00:00:00",
            "price": 199.99,
            "tags": ["wearable", "health", "gadget"],
        }

    def test_create_product_with_valid_data(self):
        """Test creating a product with valid data works."""
        product = Product(details=self.valid_product_details)
        product.save()

        # Reload from the database
        saved_product = Product.objects.get(pk=product.pk)
        details: ProductDefinition = saved_product.details

        # Check if the saved data matches the input data
        self.assertEqual(details.name, self.valid_product_details["name"])
        self.assertEqual(details.description, self.valid_product_details["description"])
        self.assertAlmostEqual(details.price, self.valid_product_details["price"])
        self.assertListEqual(details.tags, self.valid_product_details["tags"])
        self.assertEqual(
            details.created,
            datetime.fromisoformat(self.valid_product_details["created"]),
        )

    def test_create_product_with_invalid_data_raises_error(self):
        """Test that creating a product with invalid data raises a ValidationError."""
        invalid_product_details = self.valid_product_details.copy()
        invalid_product_details["price"] = "free"

        with self.assertRaises(ValidationError):
            product = Product(details=invalid_product_details)
            product.full_clean()
