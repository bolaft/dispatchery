# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Benchmarks for the dispatchery module.
"""

from functools import singledispatch

from dispatchery import dispatchery


@singledispatch
def std_with_params(value):
    return "default"


@std_with_params.register(str)
def _(value: str):
    return "str"


@singledispatch
def std_with_type_hints(value):
    return "default"


@std_with_type_hints.register
def _(value: str):
    return "str"


@dispatchery
def func_with_params(value):
    return "default."


@func_with_params.register(str)
def _(value):
    return "str"


@func_with_params.register(list[str])
def _(value):
    return "list[str]"


@func_with_params.register(tuple[str, list[str]])
def _(value):
    return "list[list[str]]"


@dispatchery
def func_with_type_hints(value):
    return "default."


@func_with_type_hints.register
def _(value: str):
    return "str"


@func_with_type_hints.register
def _(value: list[str]):
    return "list[str]"


@func_with_type_hints.register
def _(value: tuple[str, list[str]]):
    return "list[list[str]]"


def test_singledispatch_with_params(benchmark):
    result = benchmark(std_with_params, ("hello"))
    assert result == "str"


def test_singledispatch_with_type_hints(benchmark):
    result = benchmark(std_with_type_hints, ("hello"))
    assert result == "str"


def test_simple_types_with_params(benchmark):
    result = benchmark(func_with_params, ("hello"))
    assert result == "str"


def test_simple_types_with_type_hints(benchmark):
    result = benchmark(func_with_type_hints, ("hello"))
    assert result == "str"


def test_generic_types_with_params(benchmark):
    result = benchmark(func_with_params, (["hello"]))
    assert result == "list[str]"


def test_generic_types_with_type_hints(benchmark):
    result = benchmark(func_with_type_hints, (["hello"]))
    assert result == "list[str]"


def test_nested_types_with_params(benchmark):
    result = benchmark(func_with_params, (("hello", ["world"])))
    assert result == "list[list[str]]"


def test_nested_types_with_type_hints(benchmark):
    result = benchmark(func_with_type_hints, (("hello", ["world"])))
    assert result == "list[list[str]]"


def test_long_list_with_params(benchmark):
    result = benchmark(func_with_params, (["hello"] * 1000))
    assert result == "list[str]"


def test_long_list_with_type_hints(benchmark):
    result = benchmark(func_with_type_hints, (["hello"] * 1000))
    assert result == "list[str]"
