"""
Test the firestone_lib.resource module.
"""

import os
import shutil
import tempfile
import unittest

from firestone_lib import resource


class ResourceTest(unittest.TestCase):
    """Test all functions in firestone_lib.resource."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_jsonloader_file_uri(self):
        """Test _jsonloader handles file: URIs (not just file://)."""
        # Create a test JSON file
        test_file = os.path.join(self.temp_dir, "test.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write('{"test": "value"}')

        # Test with file: URI (5 characters)
        uri = f"file:{test_file}"
        # pylint: disable=protected-access
        result = resource._jsonloader(uri)
        self.assertEqual(result, {"test": "value"})

    def test_jsonloader_file_slash_slash_uri(self):
        """Test _jsonloader handles file:// URIs."""
        # Create a test JSON file
        test_file = os.path.join(self.temp_dir, "test.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write('{"test": "value"}')

        # Test with file:// URI (7 characters)
        uri = f"file://{test_file}"
        # pylint: disable=protected-access
        result = resource._jsonloader(uri)
        self.assertEqual(result, {"test": "value"})

    def test_jsonloader_yaml_with_file_ref(self):
        """Test _jsonloader handles YAML files with $ref using file: URI."""
        # Create a referenced JSON file
        ref_file = os.path.join(self.temp_dir, "reference.json")
        with open(ref_file, "w", encoding="utf-8") as f:
            f.write('{"$schema": "http://json-schema.org/draft-07/schema#", "type": "string"}')

        # Create a YAML file with a $ref using file: URI
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write(
                f"""
properties:
  test:
    $ref: "file:{ref_file}"
"""
            )

        # This should work without errors
        result = resource.get_resource_schema(yaml_file)
        self.assertIsInstance(result, dict)
        self.assertIn("properties", result)

    def test_get_resource_schema_json(self):
        """Test get_resource_schema with JSON file."""
        test_file = os.path.join(self.temp_dir, "test.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write('{"test": "value"}')

        result = resource.get_resource_schema(test_file)
        self.assertEqual(result, {"test": "value"})

    def test_get_resource_schema_yaml(self):
        """Test get_resource_schema with YAML file."""
        test_file = os.path.join(self.temp_dir, "test.yaml")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("test: value")

        result = resource.get_resource_schema(test_file)
        self.assertEqual(result, {"test": "value"})


if __name__ == "__main__":
    unittest.main()
