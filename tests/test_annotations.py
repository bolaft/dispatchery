# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Tests for the dispatchery module, using type hints.
"""

from typing import List, Dict, Tuple, Union

from dispatchery import dispatchery


def test_simple_types():
    @dispatchery
    def func(value):
        return "default"

    assert func(42) == "default"

    @func.register
    def _(value: int):
        return "int"

    @func.register
    def _(value: str):
        return "str"

    @func.register
    def _(value: list):
        return "list"

    assert func(42) == "int"
    assert func("hello") == "str"
    assert func([1, 2, 3]) == "list"
    assert func(3.14) == "default"


def test_typing_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register
    def _(value: List[int]):
        return "List[int]"

    @func.register
    def _(value: List[str]):
        return "List[str]"

    @func.register
    def _(value: Dict[str, int]):
        return "Dict[str, int]"

    @func.register
    def _(value: Tuple[int, str]):
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

    @func.register
    def _(value: int | str):
        return "int | str"

    @func.register
    def _(value: bool | float):
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

    @func.register
    def _(value: Union[int, str]):
        return "Union[int, str]"

    @func.register
    def _(value: Union[bool, float]):
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

    @func.register
    def _(value: Dummy):
        return "Dummy"

    @func.register
    def _(value: Tuple[float, Dummy]):
        return "Tuple[float, Dummy]"

    assert func(Dummy()) == "Dummy"
    assert func((1.5, Dummy())) == "Tuple[float, Dummy]"
    assert func(Dummy) == "default"
    assert func(42) == "default"


def test_parameterized_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register
    def _(value: list):
        return "List"

    @func.register
    def _(value: list[str]):
        return "List[str]"

    @func.register
    def _(value: list[int]):
        return "List[int]"

    assert func([1, 2, 3]) == "List[int]"
    assert func(["a", "b", "c"]) == "List[str]"
    assert func([1.5, 2.5, 3.5]) == "List"
    assert func(42) == "default"


def test_nested_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register
    def _(value: tuple[int, str]):
        return "Tuple[int, str]"

    @func.register
    def _(value: tuple[int, list[str]]):
        return "Tuple[int, List[str]]"

    @func.register
    def _(value: tuple[bool, Dict[str, int]]):
        return "Tuple[bool, Dict[str, int]]"

    assert func((42, "example")) == "Tuple[int, str]"
    assert func((7, ["one", "two", "three"])) == "Tuple[int, List[str]]"
    assert func((True, {"a": 1, "b": 2})) == "Tuple[bool, Dict[str, int]]"
    assert func(3.14) == "default"


def test_generic_types():
    @dispatchery
    def func(value):
        return "default"

    @func.register
    def _(value: List):
        return "List"

    @func.register
    def _(value: List[str]):
        return "List[str]"

    @func.register
    def _(value: List[int]):
        return "List[int]"

    @func.register
    def _(value: Dict):
        return "Dict"

    @func.register
    def _(value: Tuple):
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

    @func.register
    def _(value1: int, value2: str):
        return "int, str"

    @func.register
    def _(value1: bool, value2: float):
        return "bool, float"

    assert func(42, "hello") == "int, str"
    assert func(True, 3.14) == "bool, float"
    assert func(42, 3.14) == "default"
    assert func(True, "hello") == "default"


def test_optional_arguments():
    @dispatchery
    def func(value1, value2, option=None):
        return "default"

    @func.register
    def _(value1: bool, value2: int, optionp=None):
        return "bool, int, option=str"

    @func.register
    def _(value1: bool, value2: float, option: str = None):
        return "bool, float, option=str"

    @func.register
    def _(value1: bool, value2: float, option: int = None):
        return "bool, float, option=int"

    assert func(True, "hello") == "default"
    assert func(True, 3.14, option="hello") == "bool, float, option=str"
    assert func(True, 3.14, option=42) == "bool, float, option=int"
    assert func(True, 3) == "bool, int, option=str"
    assert func(True, 3.14, option=False) == "default"


def test_strict_mode():
    dispatchery.strict_mode = True

    @dispatchery
    def strict_func(value):
        return "default"

    @strict_func.register
    def _(value: list[int]):
        return "list[int]"

    @strict_func.register
    def _(value: list[str]):
        return "list[str]"

    assert strict_func([1, 2, 3]) == "list[int]"
    assert strict_func(["a", "b", "c"]) == "list[str]"

    assert strict_func([1, None, None]) == "default"
    assert strict_func(["a", None, None]) == "default"

    dispatchery.strict_mode = False

    @dispatchery
    def lenient_func(value):
        return "default"

    @lenient_func.register
    def _(value: list[int]):
        return "list[int]"

    @lenient_func.register
    def _(value: list[str]):
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

    @cached_func.register
    def _(value: int):
        return "int"

    assert cached_func("hello") == "default"
    assert cached_func(10) == "int"

    dispatchery.cache_mode = False

    @dispatchery
    def uncached_func(value):
        return "default"

    @uncached_func.register
    def _(value: int):
        return "int"

    assert uncached_func("hello") == "default"
    assert uncached_func(10) == "int"
