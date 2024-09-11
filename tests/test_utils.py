import pytest
from drive_flow import utils


def test_func_to_string():
    def my_func(a, b: str, c: float = 3.14) -> bool:
        print(a, b, c)
        return False

    func_string = """tests.test_utils.l_6
    def my_func(a, b: str, c: float = 3.14) -> bool:
        print(a, b, c)
        return False"""

    class Fool:
        def __call__(self, a, b, v):
            return a + b + v

    class_string = """tests.test_utils.l_16.Fool
        def __call__(self, a, b, v):
            return a + b + v"""

    fool_inst = Fool()
    assert utils.function_or_method_to_string(my_func) == func_string
    assert utils.function_or_method_to_string(fool_inst.__call__) == class_string


def test_func_to_repr_string():
    def my_func(a, b: str, c: float = 3.14) -> bool:
        print(a, b, c)
        return False

    func_string = """tests.test_utils.l_29.my_func"""

    class Fool:
        def __call__(self, a, b, v):
            return a + b + v

    class_string = """tests.test_utils.l_36.Fool.__call__"""

    fool_inst = Fool()
    assert utils.function_or_method_to_repr(my_func) == func_string
    assert utils.function_or_method_to_repr(fool_inst.__call__) == class_string


def test_any_to_repr_string():
    with pytest.raises(ValueError):
        utils.function_or_method_to_repr(123)

    with pytest.raises(ValueError):
        utils.function_or_method_to_string(123)
