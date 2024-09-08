from drive_events import utils


def test_func_to_string():
    def my_func(a, b: str, c: float = 3.14) -> bool:
        print(a, b, c)
        return False

    func_string = """tests.test_utils.l_5
    def my_func(a, b: str, c: float = 3.14) -> bool:
        print(a, b, c)
        return False"""

    class Fool:
        def __call__(self, a, b, v):
            return a + b + v

    class_string = """tests.test_utils.l_15.Fool
        def __call__(self, a, b, v):
            return a + b + v"""

    fool_inst = Fool()
    assert utils.function_or_method_to_string(my_func) == func_string
    assert utils.function_or_method_to_string(fool_inst.__call__) == class_string
