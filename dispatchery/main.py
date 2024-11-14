# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Dispatchery allows you to register functions for specific types, including complex 
and nested generics, such as `list[str]`, `tuple[int, str]`, or `dict[str, list[int]]`.
It inspects the input type at runtime, including nested structures, to select and call
the appropriate registered function.
"""

from functools import wraps
from typing import get_origin, get_args, Any, Callable, Type


class Dispatchery:
    """
    A dispatcher class for handling functions based on complex, parameterized types.

    Attributes:
        default_func (Callable): The default function to call if no specific type matches.
        registry (dict): A dictionary mapping types to their registered functions.
    """

    def __init__(self, func: Callable):
        """
        Initializes the Dispatchery instance with a default function.

        Args:
            func (Callable): The default function to use when no matching type is registered.
        """
        self.default_func = func
        self.registry = {}  # Dictionary to store registered types

    def register(self, type_: Type):
        """
        Decorator to register a function to handle a specific type, including generics.

        This decorator allows you to specify a function for a particular type. The function
        is added to the registry and will be called whenever the dispatch method receives
        a matching type.

        Args:
            type_ (Type): The specific type, or parameterized type, to register the function for.

        Returns:
            Callable: The decorator function for the registered type.
        """

        def decorator(func: Callable):
            self.registry[type_] = func
            return func

        return decorator

    def dispatch(self, value: Any) -> Callable:
        """
        Finds the best matching function for the given value, handling generics based on content.

        This method matches `value` to the registered functions based on its type, handling
        complex generics such as `tuple[int, str]` or `dict[str, list[int]]`. If a match
        is found, the corresponding function is returned; otherwise, the default function is used.

        Args:
            value (Any): The value to be processed, used to determine the function to call.

        Returns:
            Callable: The function that matches the type of `value`, or the default function if no match is found.
        """
        value_type = type(value)
        if value_type in self.registry:
            return self.registry[value_type]

        for registered_type, func in self.registry.items():
            origin_type = get_origin(registered_type)
            if origin_type and isinstance(value, origin_type):
                if self._check_type_recursively(value, registered_type):
                    return func

        return self.default_func

    def _check_type_recursively(self, value: Any, expected_type: Type) -> bool:
        """
        Recursively checks if `value` matches `expected_type`, handling nested generics.

        This method performs a deep check on `value` to ensure it matches `expected_type`,
        including nested and parameterized types such as `list[str]` or `dict[str, int]`.
        It supports nested structures by recursively examining each element's type.

        Args:
            value (Any): The value to check against `expected_type`.
            expected_type (Type): The expected type, possibly a generic or nested type.

        Returns:
            bool: True if `value` matches `expected_type`, False otherwise.
        """
        origin_type = get_origin(expected_type)
        if origin_type is None:
            return isinstance(value, expected_type)

        if origin_type is tuple:
            expected_args = get_args(expected_type)
            if len(value) != len(expected_args):
                return False
            return all(
                self._check_type_recursively(v, t) for v, t in zip(value, expected_args)
            )

        elif origin_type is list:
            element_type = get_args(expected_type)[0]
            return all(self._check_type_recursively(v, element_type) for v in value)

        elif origin_type is dict:
            key_type, value_type = get_args(expected_type)
            return all(
                self._check_type_recursively(k, key_type)
                and self._check_type_recursively(v, value_type)
                for k, v in value.items()
            )

        return False

    def __call__(self, value: Any, *args, **kwargs) -> Any:
        """
        Calls the appropriate function based on the type and content of `value`.

        This method dispatches `value` to the registered function that best matches
        its type, falling back to the default function if no match is found.

        Args:
            value (Any): The value to process.
            *args: Additional positional arguments to pass to the matched function.
            **kwargs: Additional keyword arguments to pass to the matched function.

        Returns:
            Any: The result from calling the matched function.
        """
        func = self.dispatch(value)
        return func(value, *args, **kwargs)


def dispatchery(func: Callable):
    """
    A decorator function that creates a Dispatchery instance for a given function.

    This decorator provides a convenient way to set up a dispatchery by wrapping
    the provided function. Additional type-specific functions can be registered
    using the `register` method on the resulting decorated function.

    Args:
        func (Callable): The function to wrap in a Dispatchery instance.

    Returns:
        Callable: A wrapper function with a `register` method to register additional type handlers.
    """
    dispatcher = Dispatchery(func)

    @wraps(func)
    def wrapper(value: Any, *args, **kwargs):
        return dispatcher(value, *args, **kwargs)

    wrapper.register = dispatcher.register
    return wrapper
