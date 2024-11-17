# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Tests for the dispatchery module, using type hints.
"""

from typing import List, Dict, Tuple, Union

from dispatchery import dispatchery


def test_simple_types():
    @dispatchery
    def func(value):
        return 0

    assert func(42) == 0

    @func.register
    def _(value: int):
        return 1

    @func.register
    def _(value: str):
        return 2

    @func.register
    def _(value: list):
        return 3

    assert func(3.14) == 0
    assert func(42) == 1
    assert func("hello") == 2
    assert func([1, 2, 3]) == 3


def test_typing_types():
    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: List[int]):
        return 1

    @func.register
    def _(value: List[str]):
        return 2

    @func.register
    def _(value: Dict[str, int]):
        return 3

    @func.register
    def _(value: Tuple[int, str]):
        return 4

    assert func(3.14) == 0
    assert func([1, 2, 3]) == 1
    assert func(["a", "b", "c"]) == 2
    assert func({"a": 1, "b": 2}) == 3
    assert func((42, "example")) == 4


def test_union_types():
    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: int | str):
        return 1

    @func.register
    def _(value: bool | float):
        return 2

    assert func([1, 2, 3]) == 0
    assert func(42) == 1
    assert func("hello") == 1
    assert func(True) == 2
    assert func(3.14) == 2


def test_optional_types():
    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: Union[int, str]):
        return 1

    @func.register
    def _(value: Union[bool, float]):
        return 2

    assert func(42) == 1
    assert func("hello") == 1
    assert func(True) == 2
    assert func(3.14) == 2


def test_classes():
    class Dummy:
        pass

    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: Dummy):
        return 1

    @func.register
    def _(value: Tuple[float, Dummy]):
        return 2

    assert func(Dummy) == 0
    assert func(42) == 0
    assert func(Dummy()) == 1
    assert func((1.5, Dummy())) == 2


def test_parameterized_types():
    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: list):
        return 1

    @func.register
    def _(value: list[str]):
        return 2

    @func.register
    def _(value: list[int]):
        return 3

    assert func(42) == 0
    assert func([1.5, 2.5, 3.5]) == 1
    assert func(["a", "b", "c"]) == 2
    assert func([1, 2, 3]) == 3


def test_nested_types():
    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: tuple[int, str]):
        return 1

    @func.register
    def _(value: tuple[int, list[str]]):
        return 2

    @func.register
    def _(value: tuple[bool, Dict[str, int]]):
        return 3

    assert func(3.14) == 0
    assert func((42, "example")) == 1
    assert func((7, ["one", "two", "three"])) == 2
    assert func((True, {"a": 1, "b": 2})) == 3


def test_generic_types():
    @dispatchery
    def func(value):
        return 0

    @func.register
    def _(value: List):
        return 1

    @func.register
    def _(value: List[str]):
        return 2

    @func.register
    def _(value: List[int]):
        return 3

    @func.register
    def _(value: Dict):
        return 4

    @func.register
    def _(value: Tuple):
        return 5

    assert func(42) == 0
    assert func([1.5, 2.5, 3.5]) == 1
    assert func(["a", "b", "c"]) == 2
    assert func([1, 2, 3]) == 3
    assert func({"a": 1, "b": 2}) == 4
    assert func((42, "example")) == 5


def test_multiple_arguments():
    @dispatchery
    def func(value1, value2):
        return 0

    @func.register
    def _(value1: int, value2: str):
        return 1

    @func.register
    def _(value1: bool, value2: float):
        return 2

    assert func(42, 3.14) == 0
    assert func(True, "hello") == 0
    assert func(42, "hello") == 1
    assert func(True, 3.14) == 2


def test_optional_arguments():
    @dispatchery
    def func(value1, value2, option=None):
        return 0

    @func.register
    def _(value1: bool, value2: int, option=None):
        return 1

    @func.register
    def _(value1: bool, value2: float, option: str = None):
        return 2

    @func.register
    def _(value1: bool, value2: float, option: int = None):
        return 3

    assert func(True, "hello") == 0
    assert func(True, 3.14, option=False) == 0
    assert func(True, 3) == 1
    assert func(True, 3.14, option="hello") == 2
    assert func(True, 3.14, option=42) == 3


def test_strict_mode():
    dispatchery.strict_mode = True

    @dispatchery
    def strict_func(value):
        return 0

    @strict_func.register
    def _(value: list[int]):
        return 1

    @strict_func.register
    def _(value: list[str]):
        return 2

    assert strict_func([1, None, None]) == 0
    assert strict_func(["a", None, None]) == 0
    assert strict_func([1, 2, 3]) == 1
    assert strict_func(["a", "b", "c"]) == 2

    dispatchery.strict_mode = False

    @dispatchery
    def lenient_func(value):
        return 0

    @lenient_func.register
    def _(value: list[int]):
        return 1

    @lenient_func.register
    def _(value: list[str]):
        return 2

    assert lenient_func([1, 2, 3]) == 1
    assert lenient_func([1, None, None]) == 1
    assert lenient_func(["a", "b", "c"]) == 2
    assert lenient_func(["a", None, None]) == 2


def test_cached_mode():
    dispatchery.cached_mode = True

    @dispatchery
    def cached_func(value):
        return 0

    @cached_func.register
    def _(value: int):
        return 1

    assert cached_func("hello") == 0
    assert cached_func(10) == 1

    dispatchery.cache_mode = False

    @dispatchery
    def uncached_func(value):
        return 0

    @uncached_func.register
    def _(value: int):
        return 1

    assert uncached_func("hello") == 0
    assert uncached_func(10) == 1
