# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Dispatchery allows you to dispatch functions based on complex, parameterized types.
It provides a decorator to register functions for specific type combinations, including
nested and generic types. The dispatcher will then call the appropriate function based
on the types of the arguments passed to it.
"""

import inspect

from functools import wraps, partial
from types import FunctionType, BuiltinFunctionType, MethodType, UnionType
from typing import get_origin, get_args, Any, Callable, Type, Tuple, Dict, Union
from inspect import signature


class Dispatchery:
    """
    A dispatcher class for handling functions based on complex, parameterized types.

    Attributes:
        default_func (Callable): The default function to call if no specific type matches.
        registry (dict): A dictionary mapping types to their registered functions.
        quick_registry (dict): A dictionary mapping simple types to their registered functions.
        strict (bool): Whether to check every dict and list element for type checking or just the first one.
    """

    def __init__(self, func: Callable, strict: bool):
        """
        Initializes the Dispatchery instance with a default function.

        Args:
            func (Callable): The default function to use when no matching type is registered.
            strict (bool): Whether to check every dict and list element for type checking or just the first one.
        """
        self.is_method = (
            len(signature(func).parameters) > 0 and "self" in signature(func).parameters
        )
        self.default_func = func
        self.registry = {}
        self.quick_registry = {}
        self.strict = strict

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
        if (
            len(types) == 1
            and not kwtypes
            and isinstance(
                func := types[0], (FunctionType, BuiltinFunctionType, MethodType)
            )
        ):
            func = self._register_from_signature(func)
            self._sort_registry()
            return func
        else:
            # Use _register_from_params for explicit type registrations
            def decorator(func: Callable):
                self._register_from_params(types, kwtypes)(func)
                # Sort registry after each registration
                self._sort_registry()
                return func

            return decorator

    def _register_from_signature(self, func: Callable):
        """
        Register a function based on its signature, inferring types from the annotations.

        Args:
            func (Callable): The function to register based on its signature.

        Returns:
            Callable: The decorated function, registered with inferred types.
        """
        sig = inspect.signature(func)

        # Gather types for positional arguments
        types = tuple(
            param.annotation
            for param in sig.parameters.values()
            if param.kind
            in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
            }
            and param.annotation is not inspect.Parameter.empty
            and param.default
            is inspect.Parameter.empty  # Exclude args with default values
        )

        # Gather types and defaults for keyword arguments (including those with defaults)
        kwtypes = {
            name: param.annotation
            for name, param in sig.parameters.items()
            if param.kind
            in {inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
            and param.default is not inspect.Parameter.empty
            and param.annotation is not inspect.Parameter.empty
        }

        # Register fast path for single positional argument
        if not kwtypes and len(types) == 1 and types[0] in (int, float, str, bool):
            self.quick_registry[types[0]] = func
        else:
            # Register the function with inferred types
            self.registry[(types, frozenset(kwtypes.items()))] = func

    def _register_from_params(self, types: Tuple[Type], kwtypes: Dict[str, Type]):
        """
        Register a function based on the provided types for positional and keyword arguments.

        Args:
            types (Tuple[Type]): The specific types for each positional argument the function should handle.
            kwtypes (Dict[str, Type]): The specific types for each keyword argument the function should handle.
        """

        def decorator(func: Callable):
            if not kwtypes and len(types) == 1 and types[0] in (int, float, str, bool):
                # Fast-path: Single argument for a single value
                self.quick_registry[types[0]] = func
            else:
                self.registry[(types, frozenset(kwtypes.items()))] = func

            return func

        return decorator

    def _sort_registry(self):
        """
        Sort the registry based on the specificity of the types.
        """
        # Avoid situations where a list[int] matches with list when list is registered first
        # List all tuples with their specificity
        tuples = [
            (self._calculate_composite_specificity(k), k, v)
            for k, v in self.registry.items()
        ]

        # Sort the tuples based on the specificity of the types
        sorted_tuples = sorted(tuples, key=lambda x: x[0], reverse=True)

        # Rebuild the registry with the sorted tuples
        self.registry = dict()
        for _, k, v in sorted_tuples:
            self.registry[k] = v

    def _calculate_composite_specificity(
        self, key: Tuple[Tuple[Type], Dict[str, Type]]
    ):
        """
        Calculate the composite specificity of a key for sorting.

        Args:
            key (Tuple[Tuple[Type], Dict[str, Type]]): The key to calculate the specificity for.

        Returns:
            Tuple[int, int, int]: A tuple containing the max specificity, sum specificity, and negative wildcard count.
        """
        arg_types, kwarg_types = key
        # Calculate specificity for positional arguments
        positional_scores = [self._calculate_specificity(t) for t in arg_types]
        # Calculate specificity for keyword arguments
        kwarg_scores = [self._calculate_specificity(t) for _, t in kwarg_types]

        # Calculate wildcards (unparameterized generics)
        wildcard_count = sum(
            1
            for t in arg_types + tuple(t for _, t in kwarg_types)
            if self._is_unparameterized_generic(t)
        )

        # Composite specificity: (max_specificity, sum_specificity, -wildcard_count)
        return (
            max(positional_scores + kwarg_scores, default=0),
            sum(positional_scores + kwarg_scores),
            -wildcard_count,
        )

    def _calculate_specificity(self, type_: Type) -> int:
        """
        Calculate the specificity of a type for sorting.
        Higher specificity means the type is more constrained.

        Args:
            type_ (Type): The type to calculate the specificity for.

        Returns:
            int: The specificity of the type.
        """
        origin = get_origin(type_)
        args = get_args(type_)

        if origin is None:
            # Simple types like int, str
            return 0
        elif args:
            # Parameterized types: add specificity for each argument
            return len(args) + sum(self._calculate_specificity(arg) for arg in args)
        else:
            return 0

    def _is_unparameterized_generic(self, type_: Type) -> bool:
        """
        Determine if a type is an unparameterized generic (used for sorting registry only).

        Args:
            type_ (Type): The type to check.

        Returns:
            bool: True if the type is an unparameterized generic, False otherwise.
        """
        origin = get_origin(type_)
        args = get_args(type_)

        return origin is not None and not args

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
        if self.is_method:
            args = args[1:]

        arg_types = tuple(map(type, args))

        if kwargs:
            kwarg_types = set()
            for k, v in kwargs.items():
                kwarg_types.add((k, type(v)))
            kwarg_types = frozenset(kwarg_types)
        else:
            if len(arg_types) == 1 and arg_types[0] in (int, float, str, bool):
                # 1. Fast-path: Single argument for a single value of single type
                try:
                    return self.quick_registry[arg_types[0]]
                except KeyError:
                    pass  # Do not return default yet, it could be a union type

        # 2. Fall back to more complex checks for parameterized and nested types
        for (
            registered_arg_types,
            registered_kwarg_types,
        ), func in self.registry.items():
            matches = []

            if self._types_match(
                args, kwargs, registered_arg_types, dict(registered_kwarg_types)
            ):
                matches.append(
                    ((registered_arg_types, dict(registered_kwarg_types)), func)
                )

            if matches:
                for params, func in matches:
                    pass  # FIXME, need to pick the most appropriate one

                return func

        # 3. Default function
        return self.default_func

    def _types_match(
        self,
        args: Tuple[Any],
        kwargs: Dict[str, Any],
        expected_arg_types: Tuple[Type],
        expected_kwarg_types: Dict[str, Type],
    ) -> bool:
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

        for arg, expected in zip(args, expected_arg_types):
            if not self._check_type_recursively(arg, expected):
                return False

        # Check if keyword arguments match
        if set(kwargs.keys()) != set(expected_kwarg_types.keys()):
            return False

        for k, expected_type in expected_kwarg_types.items():
            if not self._check_type_recursively(kwargs[k], expected_type):
                return False

        return True

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
        if expected_type is Any:
            return True

        origin_type = get_origin(expected_type)

        # If there's no origin type, expected_type is a simple (non-parameterized) type
        if origin_type is None:
            return (
                type(value) is expected_type
                if (type(value) is bool or expected_type is bool)
                else isinstance(value, expected_type)
            )

        # Check if expected_type is a Union (including the `|` syntax in Python 3.10+)
        if origin_type is Union or origin_type is UnionType:
            # Check if value matches any of the types within the Union
            return any(
                self._check_type_recursively(value, t) for t in get_args(expected_type)
            )

        # Handle tuples with nested types
        if origin_type is tuple:
            if not isinstance(value, tuple):
                return False
            expected_args = get_args(expected_type)
            if not isinstance(value, tuple) or (
                len(value) != len(expected_args) and expected_args
            ):
                return False
            return all(
                self._check_type_recursively(v, t) for v, t in zip(value, expected_args)
            )

        # Handle lists with a specific element type
        elif origin_type is list:
            if not isinstance(value, list):
                return False
            if not (args := get_args(expected_type)):
                return True  # No element type specified, so any list is valid
            element_type = args[0]
            if self.strict:
                # Check if all elements in the list match the expected type
                return isinstance(value, list) and all(
                    self._check_type_recursively(v, element_type) for v in value
                )
            else:
                # Check if the first element of the list matches the expected type
                return isinstance(value, list) and self._check_type_recursively(
                    value[0], element_type
                )

        # Handle dictionaries with specific key-value types
        elif origin_type is dict:
            if not isinstance(value, dict):
                return False
            if not (args := get_args(expected_type)):
                return True  # No key-value types specified, so any dict is valid

            key_type, value_type = args

            if self.strict:
                # Check if all keys and values in the dictionary match the expected types
                return isinstance(value, dict) and all(
                    self._check_type_recursively(k, key_type)
                    and self._check_type_recursively(v, value_type)
                    for k, v in value.items()
                )
            else:
                # Check if the first key and value in the dictionary match the expected types
                if isinstance(value, dict):
                    first_key, first_value = next(iter(value.items()))
                    return self._check_type_recursively(
                        first_key, key_type
                    ) and self._check_type_recursively(first_value, value_type)
                else:
                    return False

        # Handle types passed as values
        elif get_origin(expected_type) is not None or isinstance(value, type):
            args = get_args(expected_type)

            if args and len(args) == 1:
                try:
                    if issubclass(value, args[0]):
                        return True
                except TypeError:
                    pass

            if value == expected_type or type[value] == expected_type:
                return True
            else:
                return False

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

    def __get__(self, instance, owner):
        """
        Support instance methods by returning a bound method.
        """
        if instance is None:
            # Accessed through the class
            return self
        # Return a bound method
        return partial(self.__call__, instance)


class CachedDispatchery(Dispatchery):
    """
    A Dispatchery subclass that caches the results of type match checks.

    Attributes:
        cache (TypeMatchCache): A cache to store results of type match checks.
    """

    def __init__(self, func: Callable, strict: bool):
        super().__init__(func, strict)

        self.cache = TypeMatchCache()

    def _types_match(
        self,
        args: Tuple[Any],
        kwargs: Dict[str, Any],
        expected_arg_types: Tuple[Type],
        expected_kwarg_types: Dict[str, Type],
    ) -> bool:
        """
        Checks the types of arguments against their expected types, with caching enabled.

        Args:
            args (Tuple[Any]): The positional arguments to check.
            kwargs (Dict[str, Any]): The keyword arguments to check.
            expected_arg_types (Tuple[Type]): The expected types for positional arguments.
            expected_kwarg_types (Dict[str, Type]): The expected types for keyword arguments.

        Returns:
            bool: True if all arguments match their expected types, False otherwise.
        """
        # Check the cache first
        cached_result = self.cache.get(
            args, kwargs, expected_arg_types, expected_kwarg_types
        )

        # If the result is cached, return it
        if cached_result is not None:
            return cached_result

        # Otherwise, perform the type check
        result = super()._types_match(
            args, kwargs, expected_arg_types, expected_kwarg_types
        )

        # Cache the result
        self.cache.set(
            args, kwargs, expected_arg_types, expected_kwarg_types, value=result
        )

        # Return the result
        return result


class TypeMatchCache:
    """
    A cache to store results of type match checks for Dispatchery instances.

    This cache stores the results of type match checks for Dispatchery instances, allowing
    for faster lookups when the same types are encountered multiple times. It handles complex
    types, including nested and parameterized types, by converting them into hashable keys.

    Attributes:
        cache (Dict): A dictionary to store type match results based on the hashable keys of the arguments.
    """

    def __init__(self):
        self.cache = {}

    def _make_hashable(self, obj: Any) -> Any:
        """
        Convert potentially unhashable objects into hashable equivalents.

        Args:
            obj (Any): The object to convert into a hashable form.

        Returns:
            Any: The hashable equivalent of the input object.
        """
        if isinstance(obj, dict):
            return frozenset((k, self._make_hashable(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return tuple(self._make_hashable(i) for i in obj)
        elif isinstance(obj, tuple):
            return tuple(self._make_hashable(i) for i in obj)
        else:
            return obj

    def get(self, *args) -> Any:
        """
        Get a cached value if it exists.

        Args:
            *args: The arguments to look up in the cache.

        Returns:
            Any: The cached value if it exists, None otherwise.
        """
        hashable_args = tuple(self._make_hashable(arg) for arg in args)
        return self.cache.get(hashable_args)

    def set(self, *args, value: Any):
        """
        Set a value in the cache.

        Args:
            *args: The arguments to store in the cache.
            value (Any): The value to store in the cache.
        """
        hashable_args = tuple(self._make_hashable(arg) for arg in args)
        self.cache[hashable_args] = value


def dispatchery(func: Callable) -> Callable:
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
    cached_mode = getattr(dispatchery, "cached_mode", False)
    strict_mode = getattr(dispatchery, "strict_mode", True)

    dispatcher = (
        CachedDispatchery(func, strict_mode)
        if cached_mode
        else Dispatchery(func, strict_mode)
    )

    @wraps(func)
    def wrapper(*args, **kwargs):
        return dispatcher(*args, **kwargs)

    wrapper.register = dispatcher.register

    return wrapper
