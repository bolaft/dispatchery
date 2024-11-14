# Dispatchery 🧙‍♂️✨  
> **Dispatch your functions based on complex types.**

`dispatchery` is a very simple Python package that extends the standard `singledispatch` decorator, allowing your functions to handle complex, nested, and parameterized types. With `dispatchery`, you can dispatch based on types like `tuple[int, str, dict[str, int]]` or `list[dict[str, list[int]]]` without the need for cumbersome `isinstance` checks.

## Features

- **Advanced Type Dispatching**: Supports complex and nested generic types.
- **Recursive Type Matching**: Handles nested types like `tuple[int, str, dict[str, int]]`.
- **Simple Integration**: Works just like `functools.singledispatch` with added power.

## Installation

Install `dispatchery` from PyPI:

```bash
pip install dispatchery
```

## Usage

If you know how to use `functools.singledispatch` then you already know how to use `dispatchery`. Decorate your main function with `@dispatchery` and register specific types as needed.

### Example

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

@process.register(list[tuple[int, dict[str, tuple[list[bool], dict[str, float]]]]])
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

print(process([(1, {"a": ([True, False], {"x": 3.14})})]))
# "Now this is just getting silly."
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
