# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Tests for the dispatchery module, using parameters.
"""

from typing import List, Dict, Tuple, Union

from dispatchery import dispatchery


def test_simple_types():
    @dispatchery
    def func(value):
        return 0

    assert func(42) == 0

    @func.register(int)
    def _(value):
        return 1

    @func.register(str)
    def _(value):
        return 2

    @func.register(list)
    def _(value):
        return 3

    assert func(3.14) == 0
    assert func(42) == 1
    assert func("hello") == 2
    assert func([1, 2, 3]) == 3


def test_typing_types():
    @dispatchery
    def func(value):
        return 0

    @func.register(List[int])
    def _(value):
        return 1

    @func.register(List[str])
    def _(value):
        return 2

    @func.register(Dict[str, int])
    def _(value):
        return 3

    @func.register(Tuple[int, str])
    def _(value):
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

    @func.register(int | str)
    def _(value):
        return 1

    @func.register(bool | float)
    def _(value):
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

    @func.register(Union[int, str])
    def _(value):
        return 1

    @func.register(Union[bool, float])
    def _(value):
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

    @func.register(Dummy)
    def _(value):
        return 1

    @func.register(Tuple[float, Dummy])
    def _(value):
        return 2

    assert func(Dummy) == 0
    assert func(42) == 0
    assert func(Dummy()) == 1
    assert func((1.5, Dummy())) == 2


def test_parameterized_types():
    @dispatchery
    def func(value):
        return 0

    @func.register(list)
    def _(value):
        return 1

    @func.register(list[str])
    def _(value):
        return 2

    @func.register(list[int])
    def _(value):
        return 3

    assert func(42) == 0
    assert func([1.5, 2.5, 3.5]) == 1
    assert func(["a", "b", "c"]) == 2
    assert func([1, 2, 3]) == 3


def test_nested_types():
    @dispatchery
    def func(value):
        return 0

    @func.register(tuple[int, str])
    def _(value):
        return 1

    @func.register(tuple[int, list[str]])
    def _(value):
        return 2

    @func.register(tuple[bool, dict[str, int]])
    def _(value):
        return 3

    assert func(3.14) == 0
    assert func((42, "example")) == 1
    assert func((7, ["one", "two", "three"])) == 2
    assert func((True, {"a": 1, "b": 2})) == 3


def test_generic_types():
    @dispatchery
    def func(value):
        return 0

    @func.register(List)
    def _(value):
        return 1

    @func.register(List[str])
    def _(value):
        return 2

    @func.register(List[int])
    def _(value):
        return 3

    @func.register(Dict)
    def _(value):
        return 4

    @func.register(Tuple)
    def _(value):
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

    @func.register(int, str)
    def _(value1, value2):
        return 1

    @func.register(bool, float)
    def _(value1, value2):
        return 2

    assert func(42, 3.14) == 0
    assert func(True, "hello") == 0
    assert func(42, "hello") == 1
    assert func(True, 3.14) == 2


def test_optional_arguments():
    @dispatchery
    def func(value1, value2, option=None):
        return 0

    @func.register(bool, float, option=str)
    def _(value1, value2, option=None):
        return 1

    @func.register(int, str, option=int)
    def _(value1, value2, option=None):
        return 2

    assert func(True, "hello") == 0
    assert func(42, "hello", option=False) == 0
    assert func(True, 3.14, option="hello") == 1
    assert func(42, "hello", option=42) == 2


def test_strict_mode():
    dispatchery.strict_mode = True

    @dispatchery
    def strict_func(value):
        return 0

    @strict_func.register(list[int])
    def _(value):
        return 1

    @strict_func.register(list[str])
    def _(value):
        return 2

    assert strict_func(["a", None, None]) == 0
    assert strict_func([1, None, None]) == 0
    assert strict_func([1, 2, 3]) == 1
    assert strict_func(["a", "b", "c"]) == 2

    dispatchery.strict_mode = False

    @dispatchery
    def lenient_func(value):
        return 0

    @lenient_func.register(list[int])
    def _(value):
        return 1

    @lenient_func.register(list[str])
    def _(value):
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

    @cached_func.register(int)
    def _(value):
        return 1

    assert cached_func("hello") == 0
    assert cached_func(10) == 1

    dispatchery.cache_mode = False

    @dispatchery
    def uncached_func(value):
        return 0

    @uncached_func.register(int)
    def _(value):
        return 1

    assert uncached_func("hello") == 0
    assert uncached_func(10) == 1
