# Dispatchery 🧙‍♂️✨  
> **Dispatch your functions based on complex types.**

`dispatchery` is a lightweight Python package inspired by the standard `singledispatch` decorator, but with support for complex, nested, parameterized types. With `dispatchery`, you can dispatch based on annotations such as `tuple[int, str, dict[str, int]]` or `list[dict[str, list[int]]]`.

Unlike `singledispatch`, `dispatchery` can also dispatch based on multiple arguments and keyword arguments, rather than only the first one. It also supports nested types and union types such as `Union[int, str]` or `int | str`, making it a powerful tool for writing clean, type-specific code.

## Features

- **Advanced Type Dispatching**: Supports complex generic types.
- **Recursive Type Matching**: Handles nested types like `tuple[int, str, dict[str, int]]`.
- **Union Types**: Dispatch based on union types like `Union[int, str]`.
- **Multi Argument Dispatch**: Dispatch based on multiple arguments types, not just the first.
- **Method Overloading**: Works with object methods just the same.
- **Simple Integration**: Works just like `functools.singledispatch` with added power.

## Installation

Install `dispatchery` from PyPI:

```bash
pip install dispatchery
```

## Usage

If you know how to use `functools.singledispatch` then you already know how to use `dispatchery`. Decorate your main function with `@dispatchery` and register specific types as needed.

### Examples

Suppose we want a function, `process`, that behaves differently based on complex types like `tuple[int, str]`, `list[str]`, or `str | int`, we can use `dispatchery` to achieve this:

```python
from dispatchery import dispatchery

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
def _(value: list[tuple[int | list[float], dict[str, tuple[list[bool], dict[str, float | str]]]]]):
    return "Now this is just getting silly."

print(process(1.111))  # "Standard stuff."
print(process(["hello", "world"]))  # "Nice, a parameterized type."
print(process([1, 2, 3]))  # "That's different? Cool."
print(process([(1, "hello"), (2, "world")]))  # "Nested, too? Alright."
print(process(True))  # "Union types? No problem."
print(process([(1, {"a": ([True, False], {"x": 3.14})})]))  # "Now this is just getting silly."
```

### Multi Argument Dispatch

`dispatchery` also supports dispatching based on multiple arguments:

```python
@dispatchery
def process(a, b):
    pass

@process.register
def _(a: int, b: str):
    return "Beep boop."

@process.register
def _(a: str, b: int):
    return "Boppity bop."

print(process(42, "hello"))  # "Beep boop."
print(process("hello", 42))  # "Boppity bop."
```

### Keyword Arguments

You can also dispatch with kwargs:

```python
@dispatchery
def process(a, key="hello"):
    pass

@process.register
def _(a: str, key: int = 42):
    return "Round number."

@process.register
def _(a: str, key: float = 3.14):
    return "Decimals."

print(process("hello", key=1987))  # "Round number."
print(process("hello", key=1.618))  # "Decimals."
```

### Method Overloading

Working with classes is just as easy:

```python
from dispatchery import dispatchery


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

print(obj.my_method(42))  # "default"
print(obj.my_method([1, "a", 2, "b", 3, "c"]))  # "list"
print(obj.my_method([1, 2, 3]))  # "list[int]"
print(obj.my_method(["a", "b", "c"]))  # "list[str]"
```

### Types as Decorator Parameters

You can also pass types as arguments to the decorator instead of using type hints:

```python
@dispatchery
def process(a, b):
    pass

@process.register(int, str)
def _(a, b):
    pass

@process.register(str, int)
def _(a, b):
    pass
```

## Why Use Dispatchery?

- **Better Readability**: Your code is clean and type-specific without bulky type-checking clutter.
- **Enhanced Maintainability**: Add new types easily without modifying existing code.
- **More Flexible**: Embrace the power of Python’s dynamic typing with elegant dispatching.

## Optimizing Performance

By default `dispatchery` runs in `strict mode`. This means that it will check every value in lists and dictionaries for type matching. If you are planning to process lists of millions of items, this can be quite computationally expensive, so you may want to disable it:

```python
from dispatchery import dispatchery

dispatchery.strict_mode = False
```

This will massively speedup execution for long values, but only the first item in the list will be used for type matching.

Moreover `dispatchery` has a built-in cache that stores the type matching results. This cache is disabled by default, but you can enable it by setting the `cached_mode` attribute to `True`:

```python
from dispatchery import dispatchery

dispatchery.cached_mode = True
```

For most use cases the overhead from the cache is larger than the gains, so it's generally not worth it. But if you need to do a lot of dispatching per second with recurring complex types, it can potentially speedup `dispatchery` significantly.

## Dependencies

None, but you might want `typing-extensions>=3.7` if you need backward compatibility for typing features.

## Integration

To integrate dispatchery in an existing codebase, you can import it as a drop-in replacement for `singledispatch`:

```python
from dispatchery import dispatchery as singledispatch
```

## License

`dispatchery` is licensed under the MIT License.
