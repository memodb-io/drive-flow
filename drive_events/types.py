from dataclasses import dataclass
from typing import Union, Callable

from .utils import (
    string_to_md5_hash,
    function_or_method_to_string,
    function_or_method_to_repr,
)


class BaseNode:
    parent_groups: list[list["BaseNode"]]
    func_inst: Callable
    id: str
    repr_name: str

    def __init__(self, func_inst: Callable, parent_groups: list[list["BaseNode"]] = []):
        self.parent_groups = parent_groups
        self.func_inst = func_inst
        self.id = string_to_md5_hash(function_or_method_to_string(self.func_inst))
        self.repr_name = function_or_method_to_repr(self.func_inst)

    def debug_string(self):
        def format_parents(parents, indent=""):
            result = []
            for i, parent_group in enumerate(parents):
                is_last_group = i == len(parents) - 1
                group_prefix = "└─" if is_last_group else "├─"
                result.append(indent + group_prefix + " <listen>")
                for j, parent in enumerate(parent_group):
                    is_last = j == len(parent_group) - 1
                    child_indent = indent + ("    " if is_last_group else "│   ")
                    prefix = "└─ " if is_last else "├─ "
                    parent_debug = parent.debug_string().split("\n")
                    parent_debug = [p for p in parent_debug if p.strip()]
                    result.append(f"{child_indent}{prefix}{parent_debug[0]}")
                    for line in parent_debug[1:]:
                        result.append(f"{child_indent}   {line}")
            return "\n".join(result)

        parents_str = format_parents(self.parent_groups)
        return f"{self.repr_name}\n{parents_str}"

    def __repr__(self) -> str:
        return f"Node(source={self.repr_name})"
