# Dispatchery 🧙‍♂️✨  
> **Dispatch your functions based on complex types.**

`dispatchery` is a lightweight Python package inspired by the standard `singledispatch` decorator, but with support for complex, nested, parameterized types. With `dispatchery`, you can dispatch based on annotations such as `tuple[int, str, dict[str, int]]` or `list[dict[str, list[int]]]`.

Unlike `singledispatch`, `dispatchery` can also dispatch based on multiple arguments and keyword arguments, rather than only the first one. It also supports nested types and union types such as `Union[int, str]` or `int | str`, making it a powerful tool for writing clean, type-specific code.

## Features

- **Advanced Type Dispatching**: Supports complex and nested generic types.
- **Recursive Type Matching**: Handles nested types like `tuple[int, str, dict[str, int]]`.
- **Union Types**: Dispatch based on union types like `Union[int, str]`.
- **Multi Argument Dispatch**: Dispatch based on multiple arguments types, not just the first.
- **Simple Integration**: Works just like `functools.singledispatch` with added power.

## Installation

Install `dispatchery` from PyPI:

```bash
pip install dispatchery
```

## Usage

If you know how to use `functools.singledispatch` then you already know how to use `dispatchery`. Decorate your main function with `@dispatchery` and register specific types as needed.

### Examples

Suppose we want a function, `process`, that behaves differently based on complex types like `tuple[int, str]`, `list[str]`, or `dict[str, int]`. It also works with nested types like `list[tuple[int, dict[str, float]]]`.

```python
from dispatchery import dispatchery

@dispatchery
def process(value):
    return "Standard stuff."

@process.register(list[str])
def _(value):
    return "Nice, a parameterized type."

@process.register(list[int])
def _(value):
    return "That's different? Cool."

@process.register(list[tuple[int, str]])
def _(value):
    return "Nested, too? Alright."

@process.register(bool | str | int)
def _(value):
    return "Union types? No problem."

@process.register(list[tuple[int | list[float], dict[str, tuple[list[bool], dict[str, float | str]]]]])
def _(value):
    return "Now this is just getting silly."


print(process(42))
# "Standard stuff."

print(process(["hello", "world"]))
# "Nice, a parameterized type."

print(process([1, 2, 3]))
# "That's different? Cool."

print(process([(1, "hello"), (2, "world")]))
# "Nested, too? Alright."

print(process(True))
# "Union types? No problem."

print(process([(1, {"a": ([True, False], {"x": 3.14})})]))
# "Now this is just getting silly."
```

`dispatchery` also supports dispatching based on multiple arguments:

```python
@dispatchery
def process(a, b):
    pass

@process.register(int, str)
def _(a, b):
    return "Bip boop."

@process.register(str, int)
def _(a, b):
    return "Boopidy bop."

print(process(42, "hello"))
# "Bip boop."

print(process("hello", 42))
# "Boopidy bop."
```

And even dispatching with kwargs:

```python
@dispatchery
def process(a, key="hello"):
    pass

@process.register(str, key=int)
def _(a, key=42):
    return "I like round numbers."

@process.register(str, key=float)
def _(a, key=3.14):
    return "Floats are fine too I guess."

print(process("hello", key=1987))
# "I like round numbers."

print(process("hello", key=1.618))
# "Floats are fine too I guess."
```

## Why Use Dispatchery?

- **Better Readability**: Your code is clean and type-specific without bulky `if` statements.
- **Enhanced Maintainability**: Add new types easily without modifying existing code.
- **More Pythonic**: Embrace the power of Python’s dynamic typing with elegant dispatching.

## Dependencies

None, but you might want `typing-extensions>=3.7` if you need backward compatibility for typing features.

## Tip

To integrate dispatchery in an existing codebase, you can import it as `singledispatch` for a seamless transition:

```python
from dispatchery import dispatchery as singledispatch
```

## License

`dispatchery` is licensed under the MIT License.
