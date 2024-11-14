# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Tests for the dispatchery module.
"""

from typing import Union

from dispatchery import dispatchery


class Dummy:
    def __init__(self):
        self.value = "I'm a dummy"


@dispatchery
def process(value):
    return f"Default processing for {type(value).__name__}"


@process.register(int)
def _(value):
    return f"Processing an integer: {value}"


@process.register(str)
def _(value):
    return f"Processing a string: {value}"


@process.register(Dummy)
def _(value):
    return f"Processing a Dummy instance: {value.value}"


@process.register(list[str])
def _(value):
    return f"Processing a list of strings with {len(value)} elements"


@process.register(list[bool])
def _(value):
    return f"Processing a list of booleans with {len(value)} elements"


@process.register(tuple[float, Dummy])
def _(value):
    return f"Processing a tuple with a float and a Dummy instance: ({value[0]}, {value[1].value})"


@process.register(tuple[int, str])
def _(value):
    return f"Processing a tuple with an integer and a string: {value}"


@process.register(tuple[int, list[str]])
def _(value):
    return f"Processing a nested tuple: integer and list of strings with {len(value[1])} elements"


@process.register(dict[str, int])
def _(value):
    return (
        "Processing a dictionary with string keys and integer values."
    )

@process.register(bool, str, list[dict])
def _(value1, value2, value3):
    return "Processing a bool, a string, and a list of dictionaries"


@process.register(bool, str, option=list[int])
def _(value1, value2, option=[1, 2, 3]):
    return "Processing a bool, a string, and an optional list of integers"


@process.register(bool, str, option=list[dict])
def _(value1, value2, option=[{"a": 1, "b": 2}]):
    return "Processing a bool, a string, and an optional list of dictionaries"

@process.register(int, bool | str)
def _(value1, value2):
    return "Processing an integer and a boolean or string"

@process.register(int, Union[float, str])
def _(value1, value2):
    return "Processing an integer and a float or string"

def test_default():
    assert process(3.14) == "Default processing for float"
    assert process(True) == "Default processing for bool"


def test_regular_types():
    assert process(10) == "Processing an integer: 10"
    assert process("hello") == "Processing a string: hello"


def test_classes():
    assert process(Dummy) == "Default processing for type"
    assert process(Dummy()) == "Processing a Dummy instance: I'm a dummy"
    assert (
        process((1.5, Dummy()))
        == "Processing a tuple with a float and a Dummy instance: (1.5, I'm a dummy)"
    )


def test_generic_types():
    assert (
        process(["apple", "banana"]) == "Processing a list of strings with 2 elements"
    )
    assert (
        process([True, False, True]) == "Processing a list of booleans with 3 elements"
    )


def test_nested_generic_types():
    assert (
        process((42, "example"))
        == "Processing a tuple with an integer and a string: (42, 'example')"
    )
    assert (
        process((7, ["one", "two", "three"]))
        == "Processing a nested tuple: integer and list of strings with 3 elements"
    )


def test_dictionary_generic_type():
    assert (
        process({"a": 5, "b": 15})
        == "Processing a dictionary with string keys and integer values."
    )

def test_multiple_types():
    assert (
        process(True, "hello", [{"a": 1, "b": 2}])
        == "Processing a bool, a string, and a list of dictionaries"
    )

def test_options():
    assert (
        process(True, "hello", option=[{"a": 1, "b": 2}])
        == "Processing a bool, a string, and an optional list of dictionaries"
    )
    assert (
        process(True, "hello", option=[1, 2, 3])
        == "Processing a bool, a string, and an optional list of integers"
    )

def test_union():
    assert (
        process(42, True) == "Processing an integer and a boolean or string"
    )
    assert (
        process(42, 3.14) == "Processing an integer and a float or string"
    )