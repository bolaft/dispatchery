from functools import wraps
from typing import get_origin, get_args, Any, Callable, Type, Tuple, Dict, Union


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
        self.registry = {}  # Dictionary to store registered type combinations for args and kwargs

    def register(self, *types: Tuple[Type], **kwtypes: Dict[str, Type]):
        """
        Decorator to register a function to handle specific types across multiple arguments.

        This decorator allows you to specify a function for a particular set of positional
        and keyword argument types. The function is added to the registry and will be called
        whenever the dispatch method receives matching types.

        Args:
            *types (Tuple[Type]): The specific types for each positional argument the function should handle.
            **kwtypes (Dict[str, Type]): The specific types for each keyword argument the function should handle.

        Returns:
            Callable: The decorator function for the registered types.
        """
        def decorator(func: Callable):
            self.registry[(types, frozenset(kwtypes.items()))] = func
            return func
        return decorator

    def dispatch(self, *args, **kwargs) -> Callable:
        """
        Finds the best matching function for the given arguments based on their types.

        This method matches `args` and `kwargs` to the registered functions based on their
        types, including parameterized and nested types. If a match is found, the corresponding
        function is returned; otherwise, the default function is used.

        Args:
            *args: Positional arguments used to determine the function to call.
            **kwargs: Keyword arguments used to determine the function to call.

        Returns:
            Callable: The function that matches the types of `args` and `kwargs`, or the
            default function if no match is found.
        """
        arg_types = tuple(type(arg) for arg in args)
        kwarg_types = frozenset((k, type(v)) for k, v in kwargs.items())

        # Check for an exact match first (without considering subclasses)
        if (arg_types, kwarg_types) in self.registry:
            return self.registry[(arg_types, kwarg_types)]

        # Check for parameterized type matches, including subclasses
        for (registered_arg_types, registered_kwarg_types), func in self.registry.items():
            if self._types_match(args, kwargs, registered_arg_types, dict(registered_kwarg_types)):
                return func

        return self.default_func

    def _types_match(self, args: Tuple[Any], kwargs: Dict[str, Any], expected_arg_types: Tuple[Type], expected_kwarg_types: Dict[str, Type]) -> bool:
        """
        Check if each argument (positional and keyword) matches its expected type, allowing for complex generics.

        Args:
            args (Tuple[Any]): The positional arguments to check.
            kwargs (Dict[str, Any]): The keyword arguments to check.
            expected_arg_types (Tuple[Type]): The expected types for positional arguments.
            expected_kwarg_types (Dict[str, Type]): The expected types for keyword arguments.

        Returns:
            bool: True if all arguments match their expected types, False otherwise.
        """
        # Check if positional arguments match
        if len(args) != len(expected_arg_types):
            return False
        if not all(self._check_type_recursively(arg, expected) for arg, expected in zip(args, expected_arg_types)):
            return False

        # Check if keyword arguments match
        if set(kwargs.keys()) != set(expected_kwarg_types.keys()):
            return False
        return all(self._check_type_recursively(kwargs[k], expected_type) for k, expected_type in expected_kwarg_types.items())

    def _check_type_recursively(self, value: Any, expected_type: Type) -> bool:
        """
        Recursively checks if `value` matches `expected_type`, handling nested generics, Union, and | types.

        This method performs a deep check on `value` to ensure it matches `expected_type`, including nested
        and parameterized types such as `list[str]`, `tuple[int, str]`, `Union[int, str]`, or `int | str`.
        It supports both regular and nested structures by recursively examining each element's type.

        Args:
            value (Any): The value to check against `expected_type`.
            expected_type (Type): The expected type, possibly a generic, Union, or nested type.

        Returns:
            bool: True if `value` matches `expected_type`, False otherwise.
        """
        origin_type = get_origin(expected_type)
        
        # Check if expected_type is a Union (including the `|` syntax in Python 3.10+)
        if origin_type is Union:
            # Check if value matches any of the types within the Union
            return any(self._check_type_recursively(value, t) for t in get_args(expected_type))

        # If there's no origin type, expected_type is a simple (non-parameterized) type.
        if origin_type is None:
            return type(value) is expected_type if (type(value) is bool or expected_type is bool) else isinstance(value, expected_type)

        # Handle tuples with nested types
        if origin_type is tuple:
            expected_args = get_args(expected_type)
            if not isinstance(value, tuple) or len(value) != len(expected_args):
                return False
            return all(
                self._check_type_recursively(v, t) for v, t in zip(value, expected_args)
            )

        # Handle lists with a specific element type
        elif origin_type is list:
            element_type = get_args(expected_type)[0]
            return isinstance(value, list) and all(
                self._check_type_recursively(v, element_type) for v in value
            )

        # Handle dictionaries with specific key-value types
        elif origin_type is dict:
            key_type, value_type = get_args(expected_type)
            return isinstance(value, dict) and all(
                self._check_type_recursively(k, key_type)
                and self._check_type_recursively(v, value_type)
                for k, v in value.items()
            )

        # Fallback to regular isinstance check for non-container types
        return isinstance(value, expected_type)

    def __call__(self, *args, **kwargs) -> Any:
        """
        Calls the appropriate function based on the types of `args` and `kwargs`.

        This method dispatches `args` and `kwargs` to the registered function that best matches
        their types, falling back to the default function if no match is found.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result from calling the matched function.
        """
        func = self.dispatch(*args, **kwargs)
        return func(*args, **kwargs)


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
    def wrapper(*args, **kwargs):
        return dispatcher(*args, **kwargs)

    wrapper.register = dispatcher.register
    return wrapper
