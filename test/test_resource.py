"""
Tests for firestone_lib.resource helpers.
"""

import json
import tempfile
from pathlib import Path

import unittest
from unittest import mock

import jsonschema
import yaml

import firestone_lib
from firestone_lib import resource

_ = firestone_lib.__name__


class ResourceTest(unittest.TestCase):
    """Exercise schema loader utilities."""

    def test_jsonloader_supports_json_and_yaml(self) -> None:
        """_jsonloader reads JSON directly and YAML via jsonref conversion."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = Path(tmp_dir, "schema.json")
            yaml_path = Path(tmp_dir, "schema.yaml")

            json_path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
            yaml_path.write_text("foo: bar", encoding="utf-8")

            # Accessing _jsonloader is intentional to verify loader behavior.
            # pylint: disable=protected-access
            self.assertEqual(resource._jsonloader(str(json_path)), {"foo": "bar"})
            self.assertEqual(resource._jsonloader(f"file://{json_path}"), {"foo": "bar"})
            self.assertEqual(resource._jsonloader(str(yaml_path)), {"foo": "bar"})
            self.assertEqual(resource._jsonloader(f"file://{yaml_path}"), {"foo": "bar"})

    def test_get_resource_schema_reads_json_document(self) -> None:
        """get_resource_schema reads JSON documents via jsonref."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = Path(tmp_dir, "schema.json")
            json_path.write_text(json.dumps({"title": "sample"}), encoding="utf-8")

            self.assertEqual(
                resource.get_resource_schema(str(json_path)),
                {"title": "sample"},
            )

    def test_get_resource_schema_returns_parsed_data(self) -> None:
        """get_resource_schema parses YAML and resolves references."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir, "root.yaml")
            referenced = Path(tmp_dir, "child.json")

            referenced.write_text(json.dumps({"baz": "qux"}), encoding="utf-8")
            target.write_text(
                yaml.safe_dump({"child": {"$ref": referenced.name}}),
                encoding="utf-8",
            )

            data = resource.get_resource_schema(str(target))

            self.assertEqual(data["child"]["baz"], "qux")

    def test_validate_loads_schema_and_invokes_jsonschema(self) -> None:
        """validate pulls the packaged schema and delegates to jsonschema.validate."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = Path(tmp_dir, "resource.yaml")
            schema_path.write_text(
                yaml.safe_dump(
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    }
                ),
                encoding="utf-8",
            )

            class FakeTraversable:
                """Minimal resource wrapper for patching resource access."""

                def joinpath(self, name: str):
                    """Replicate Traversable.joinpath for the test schema."""
                    if name != "resource.yaml":
                        raise AssertionError(name)
                    return self

                def open(self, mode: str, encoding: str):
                    """Return a file handle to the schema fixture."""
                    return schema_path.open(mode, encoding=encoding)

            with mock.patch("importlib.resources.files", return_value=FakeTraversable()):
                with mock.patch("firestone_lib.resource.jsonschema.validate") as validate_mock:
                    resource.validate({"name": "firestone"})

            validate_mock.assert_called_once()
            _, kwargs = validate_mock.call_args
            self.assertEqual(kwargs["instance"], {"name": "firestone"})
            self.assertEqual(kwargs["schema"], resource.get_resource_schema(str(schema_path)))

    def test_validate_propagates_validation_error(self) -> None:
        """validate surfaces jsonschema ValidationError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = Path(tmp_dir, "resource.yaml")
            schema_path.write_text(
                yaml.safe_dump(
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    }
                ),
                encoding="utf-8",
            )

            class FakeTraversable:
                """Minimal resource wrapper for patching resource access."""

                def joinpath(self, name: str):
                    """Replicate Traversable.joinpath for the test schema."""
                    if name != "resource.yaml":
                        raise AssertionError(name)
                    return self

                def open(self, mode: str, encoding: str):
                    """Return a file handle to the schema fixture."""
                    return schema_path.open(mode, encoding=encoding)

            with mock.patch("importlib.resources.files", return_value=FakeTraversable()):
                with mock.patch(
                    "firestone_lib.resource.jsonschema.validate",
                    side_effect=jsonschema.exceptions.ValidationError("boom"),
                ):
                    with self.assertRaises(jsonschema.exceptions.ValidationError):
                        resource.validate({"name": 42})


if __name__ == "__main__":
    unittest.main()
