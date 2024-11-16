# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Tests for the dispatchery module, using parameters.
"""

from typing import List, Dict, Tuple, Union

from dispatchery import dispatchery


def test_simple_types():
    @dispatchery
    def func(value):
        return "default"

    assert func(42) == "default"

    @func.register(int)
    def _(value):
        return "int"

    @func.register(str)
    def _(value):
        return "str"

    @func.register(list)
    def _(value):
        return "list"

    assert func(42) == "int"
    assert func("hello") == "str"
    assert func([1, 2, 3]) == "list"
    assert func(3.14) == "default"


def test_typing_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register(List[int])
    def _(value):
        return "List[int]"

    @func.register(List[str])
    def _(value):
        return "List[str]"

    @func.register(Dict[str, int])
    def _(value):
        return "Dict[str, int]"

    @func.register(Tuple[int, str])
    def _(value):
        return "Tuple[int, str]"

    assert func([1, 2, 3]) == "List[int]"
    assert func(["a", "b", "c"]) == "List[str]"
    assert func({"a": 1, "b": 2}) == "Dict[str, int]"
    assert func((42, "example")) == "Tuple[int, str]"
    assert func(3.14) == "default"


def test_union_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register(int | str)
    def _(value):
        return "int | str"

    @func.register(bool | float)
    def _(value):
        return "bool | float"

    assert func(42) == "int | str"
    assert func("hello") == "int | str"
    assert func(True) == "bool | float"
    assert func(3.14) == "bool | float"
    assert func([1, 2, 3]) == "default"


def test_optional_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register(Union[int, str])
    def _(value):
        return "Union[int, str]"

    @func.register(Union[bool, float])
    def _(value):
        return "Union[bool, float]"

    assert func(42) == "Union[int, str]"
    assert func("hello") == "Union[int, str]"
    assert func(True) == "Union[bool, float]"
    assert func(3.14) == "Union[bool, float]"


def test_classes():
    class Dummy:
        pass

    @dispatchery
    def func(value):
        return "default"

    @func.register(Dummy)
    def _(value):
        return "Dummy"

    @func.register(Tuple[float, Dummy])
    def _(value):
        return "Tuple[float, Dummy]"

    assert func(Dummy()) == "Dummy"
    assert func((1.5, Dummy())) == "Tuple[float, Dummy]"
    assert func(Dummy) == "default"
    assert func(42) == "default"


def test_parameterized_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register(list)
    def _(value):
        return "List"

    @func.register(list[str])
    def _(value):
        return "List[str]"

    @func.register(list[int])
    def _(value):
        return "List[int]"

    assert func([1, 2, 3]) == "List[int]"
    assert func(["a", "b", "c"]) == "List[str]"
    assert func([1.5, 2.5, 3.5]) == "List"
    assert func(42) == "default"


def test_nested_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register(tuple[int, str])
    def _(value):
        return "Tuple[int, str]"

    @func.register(tuple[int, list[str]])
    def _(value):
        return "Tuple[int, List[str]]"

    @func.register(tuple[bool, Dict[str, int]])
    def _(value):
        return "Tuple[bool, Dict[str, int]]"

    assert func((42, "example")) == "Tuple[int, str]"
    assert func((7, ["one", "two", "three"])) == "Tuple[int, List[str]]"
    assert func((True, {"a": 1, "b": 2})) == "Tuple[bool, Dict[str, int]]"
    assert func(3.14) == "default"


def test_generic_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register(List)
    def _(value):
        return "List"

    @func.register(List[str])
    def _(value):
        return "List[str]"

    @func.register(List[int])
    def _(value):
        return "List[int]"

    @func.register(Dict)
    def _(value):
        return "Dict"

    @func.register(Tuple)
    def _(value):
        return "Tuple"

    assert func(["a", "b", "c"]) == "List[str]"
    assert func([1, 2, 3]) == "List[int]"
    assert func([1.5, 2.5, 3.5]) == "List"
    assert func({"a": 1, "b": 2}) == "Dict"
    assert func((42, "example")) == "Tuple"
    assert func(42) == "default"


def test_multiple_arguments():
    @dispatchery
    def func(value1, value2):
        return "default"

    @func.register(int, str)
    def _(value1, value2):
        return "int, str"

    @func.register(bool, float)
    def _(value1, value2):
        return "bool, float"

    assert func(42, "hello") == "int, str"
    assert func(True, 3.14) == "bool, float"
    assert func(42, 3.14) == "default"
    assert func(True, "hello") == "default"


def test_optional_arguments():
    @dispatchery
    def func(value1, value2, option=None):
        return "default"

    @func.register(bool, float, option=str)
    def _(value1, value2, option=None):
        return "bool, float, option=str"

    @func.register(int, str, option=int)
    def _(value1, value2, option=None):
        return "int, str, option=int"

    assert func(True, "hello") == "default"
    assert func(True, 3.14, option="hello") == "bool, float, option=str"
    assert func(42, "hello", option=42) == "int, str, option=int"
    assert func(42, "hello", option=False) == "default"


def test_strict_mode():
    dispatchery.strict_mode = True

    @dispatchery
    def strict_func(value):
        return "default"

    @strict_func.register(list[int])
    def _(value):
        return "list[int]"

    @strict_func.register(list[str])
    def _(value):
        return "list[str]"

    assert strict_func([1, 2, 3]) == "list[int]"
    assert strict_func(["a", "b", "c"]) == "list[str]"

    assert strict_func([1, None, None]) == "default"
    assert strict_func(["a", None, None]) == "default"

    dispatchery.strict_mode = False

    @dispatchery
    def lenient_func(value):
        return "default"

    @lenient_func.register(list[int])
    def _(value):
        return "list[int]"

    @lenient_func.register(list[str])
    def _(value):
        return "list[str]"

    assert lenient_func([1, 2, 3]) == "list[int]"
    assert lenient_func(["a", "b", "c"]) == "list[str]"

    assert lenient_func([1, None, None]) == "list[int]"
    assert lenient_func(["a", None, None]) == "list[str]"


def test_cached_mode():
    dispatchery.cached_mode = True

    @dispatchery
    def cached_func(value):
        return "default"

    @cached_func.register(int)
    def _(value):
        return "int"

    assert cached_func("hello") == "default"
    assert cached_func(10) == "int"

    dispatchery.cache_mode = False

    @dispatchery
    def uncached_func(value):
        return "default"

    @uncached_func.register(int)
    def _(value):
        return "int"

    assert uncached_func("hello") == "default"
    assert uncached_func(10) == "int"
