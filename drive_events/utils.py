import logging
import asyncio
import inspect
import hashlib

logger = logging.getLogger("drive-events")


def always_get_a_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def function_or_method_to_repr(func_or_method: callable) -> str:
    module = func_or_method.__module__
    name = func_or_method.__name__
    line_number = inspect.getsourcelines(func_or_method)[1]

    if inspect.ismethod(func_or_method):
        class_name = func_or_method.__self__.__class__.__name__
        return f"{module}.l_{line_number}.{class_name}.{name}".strip()
    elif inspect.isfunction(func_or_method):
        return f"{module}.l_{line_number}.{name}".strip()
    else:
        raise ValueError("Input must be a function or method")


def function_or_method_to_string(func_or_method: callable) -> str:
    module = func_or_method.__module__
    source = inspect.getsource(func_or_method)
    line_number = inspect.getsourcelines(func_or_method)[1]

    if inspect.ismethod(func_or_method):
        class_name = func_or_method.__self__.__class__.__name__
        return f"{module}.l_{line_number}.{class_name}\n{source}".strip()
    elif inspect.isfunction(func_or_method):
        return f"{module}.l_{line_number}\n{source}".strip()
    else:
        raise ValueError("Input must be a function or method")


def string_to_md5_hash(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()