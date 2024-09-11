import uuid
import logging
import asyncio
import inspect
import hashlib
from typing import Callable

logger = logging.getLogger("drive-flow")


def generate_uuid() -> str:
    return str(uuid.uuid4())


def function_or_method_to_repr(func_or_method: Callable) -> str:
    is_method = inspect.ismethod(func_or_method)
    is_function = inspect.isfunction(func_or_method)
    if not is_method and not is_function:
        raise ValueError("Input must be a function or method")
    module = func_or_method.__module__
    name = func_or_method.__name__
    line_number = inspect.getsourcelines(func_or_method)[1]

    if is_method:
        class_name = func_or_method.__self__.__class__.__name__
        return f"{module}.l_{line_number}.{class_name}.{name}".strip()
    else:
        return f"{module}.l_{line_number}.{name}".strip()


def function_or_method_to_string(func_or_method: Callable) -> str:
    is_method = inspect.ismethod(func_or_method)
    is_function = inspect.isfunction(func_or_method)
    if not is_method and not is_function:
        raise ValueError("Input must be a function or method")
    module = func_or_method.__module__
    source = inspect.getsource(func_or_method)
    line_number = inspect.getsourcelines(func_or_method)[1]

    if is_method:
        class_name = func_or_method.__self__.__class__.__name__
        return f"{module}.l_{line_number}.{class_name}\n{source}".strip()
    else:
        return f"{module}.l_{line_number}\n{source}".strip()


def string_to_md5_hash(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()
