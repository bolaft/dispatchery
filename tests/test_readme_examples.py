# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Tests for the dispatchery README examples.
"""

from dispatchery import dispatchery


def test_main_example():
    @dispatchery
    def process(value):
        return "Standard stuff."

    @process.register
    def _(value: list[str]):
        return "Nice, a parameterized type."

    @process.register
    def _(value: list[int]):
        return "That's different? Cool."

    @process.register
    def _(value: list[tuple[int, str]]):
        return "Nested, too? Alright."

    @process.register
    def _(value: bool | str | int):
        return "Union types? No problem."

    @process.register
    def _(
        value: list[
            tuple[
                int | list[float], dict[str, tuple[list[bool], dict[str, float | str]]]
            ]
        ]
    ):
        return "Now this is just getting silly."

    assert process(1.11) == "Standard stuff."
    assert process(["hello", "world"]) == "Nice, a parameterized type."
    assert process([1, 2, 3]) == "That's different? Cool."
    assert process([(1, "hello"), (2, "world")]) == "Nested, too? Alright."
    assert process(True) == "Union types? No problem."
    assert (
        process([(1, {"a": ([True, False], {"x": 3.14})})])
        == "Now this is just getting silly."
    )


def test_multi_arg_example():
    @dispatchery
    def process(a, b):
        pass

    @process.register
    def _(a: int, b: str):
        return "Beep boop."

    @process.register
    def _(a: str, b: int):
        return "Boppity bop."

    assert process(42, "hello") == "Beep boop."
    assert process("hello", 42) == "Boppity bop."


def test_kwarg_example():
    @dispatchery
    def process(a, key="hello"):
        pass

    @process.register
    def _(a: str, key: int = 42):
        return "Round number."

    @process.register
    def _(a: str, key: float = 3.14):
        return "Decimals."

    assert process("hello", key=1987) == "Round number."
    assert process("hello", key=1.618) == "Decimals."


def test_decorator_parameters_example():
    @dispatchery
    def process(a, b):
        pass

    @process.register(int, str)
    def _(a, b):
        return 1

    @process.register(str, int)
    def _(a, b):
        return 2

    assert process(42, "hello") == 1
    assert process("hello", 42) == 2


def test_classes_example():
    class MyClass:
        @dispatchery
        def my_method(self, value1):
            return "default"

        @my_method.register
        def _(self, value1: list):
            return "list"

        @my_method.register
        def _(self, value1: list[int]):
            return "list[int]"

        @my_method.register
        def _(self, value1: list[str]):
            return "list[str]"

    obj = MyClass()

    assert obj.my_method(42) == "default"
    assert obj.my_method([True, False]) == "list"
    assert obj.my_method([1, 2, 3]) == "list[int]"
    assert obj.my_method(["a", "b", "c"]) == "list[str]"
