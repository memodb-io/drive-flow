from drive_events.types import BaseNode


def test_node_hash():
    def mock_a():
        return 1

    def mock_b():
        return 2

    n1 = BaseNode(mock_a)
    n2 = BaseNode(mock_a)
    n3 = BaseNode(mock_b)
    assert n1.id == n2.id
    assert n1.id != n3.id


def test_node_debug_print():
    def mock_a():
        return 1

    def mock_b():
        return 2

    n1 = BaseNode(mock_a)
    n2 = BaseNode(mock_a, parent_groups=[[n1, n1]])
    n3 = BaseNode(mock_b, parent_groups=[[n1], [n2]])

    print(n1.debug_string())
    print(n2.debug_string())
    print(n3.debug_string())
