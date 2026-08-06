import json

from clifunction import Targets


class TestSchema:

    @staticmethod
    def two():
        """two docs"""
        return "two!"

    @staticmethod
    def some_args(*, arg: str = "hi"):
        """docs"""
        return arg

    @staticmethod
    # pylint: disable=unused-argument
    def complex_method(*, required_str: str, optional_bool: bool = False):
        """has both a required and an optional arg"""
        return "complex"

    def test_zero_arg_target(self):
        t = Targets()
        t.add_target(self.two)
        assert t.schema() == [{
            "name": "two",
            "abbreviations": ["two", "t"],
            "docstring": "two docs",
            "args": [],
        }]

    def test_optional_arg_target(self):
        t = Targets()
        t.add_target(self.some_args)
        schema = t.schema()
        assert len(schema) == 1
        assert schema[0]["args"] == [{
            "name": "arg",
            "abbreviations": ["arg", "a"],
            "type": "str",
            "default": "hi",
            "required": False,
        }]

    def test_required_vs_optional_flag(self):
        t = Targets()
        t.add_target(self.complex_method)
        args_by_name = {a["name"]: a for a in t.schema()[0]["args"]}
        assert args_by_name["required_str"]["required"] is True
        assert args_by_name["required_str"]["default"] is None
        assert args_by_name["optional_bool"]["required"] is False
        assert args_by_name["optional_bool"]["default"] is False

    def test_output_is_json_serializable(self):
        t = Targets()
        t.add_target(self.two)
        t.add_target(self.complex_method)
        # schema() promises a JSON-serializable structure -- prove it, don't just assert shape.
        round_tripped = json.loads(json.dumps(t.schema()))
        assert round_tripped == t.schema()

    def test_multiple_targets_preserve_registration_order(self):
        t = Targets()
        t.add_target(self.complex_method)
        t.add_target(self.two)
        assert [entry["name"] for entry in t.schema()] == ["complex_method", "two"]
