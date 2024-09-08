from copy import copy
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from .utils import (
    string_to_md5_hash,
    function_or_method_to_string,
    function_or_method_to_repr,
)

GroupEventReturns = dict["BaseEvent", Any]
EventInput = tuple[str, GroupEventReturns]

EventFunction = Callable[[EventInput], Awaitable[Any]]


@dataclass
class EventGroup:
    name: str
    events: list["BaseEvent"]

    def __post_init__(self):
        self.events = sorted(self.events, key=lambda e: e.id)
        self._hash = string_to_md5_hash(":".join([e.id for e in self.events]))

    def hash(self) -> str:
        return self._hash


class BaseEvent:
    parent_groups: dict[str, EventGroup]
    func_inst: Callable
    id: str
    repr_name: str

    def __init__(
        self,
        func_inst: Callable,
        parent_groups: dict[str, EventGroup] = None,
    ):
        self.parent_groups = parent_groups or {}
        self.func_inst = func_inst
        self.id = string_to_md5_hash(function_or_method_to_string(self.func_inst))
        self.repr_name = function_or_method_to_repr(self.func_inst)

    def debug_string(self, exclude_events: set[str] = None) -> str:
        exclude_events = exclude_events or set([self.id])

        def format_parents(parents: dict[str, EventGroup], indent=""):
            result = []
            for i, parent_group in enumerate(parents.values()):
                is_last_group = i == len(parents) - 1
                group_prefix = "└─ " if is_last_group else "├─ "
                result.append(indent + group_prefix + f"<{parent_group.name}>")
                for j, parent in enumerate(parent_group.events):
                    root_events = copy(exclude_events)
                    is_last = j == len(parent_group.events) - 1
                    child_indent = indent + ("    " if is_last_group else "│   ")
                    inter_indent = "   " if is_last else "│  "
                    prefix = "└─ " if is_last else "├─ "

                    if parent.id in root_events:
                        result.append(
                            f"{child_indent}{prefix}{parent.repr_name} <loop>"
                        )
                        continue
                    root_events.add(parent.id)
                    parent_debug = parent.debug_string(
                        exclude_events=root_events
                    ).split("\n")
                    parent_debug = [p for p in parent_debug if p.strip()]
                    result.append(f"{child_indent}{prefix}{parent.repr_name}")
                    for line in parent_debug[1:]:
                        result.append(f"{child_indent}{inter_indent}{line}")
            return "\n".join(result)

        parents_str = format_parents(self.parent_groups)
        return f"{self.repr_name}\n{parents_str}"

    def __repr__(self) -> str:
        return f"Node(source={self.repr_name})"

    async def solo_run(self, event_input: EventInput) -> Awaitable[Any]:
        return await self.func_inst(event_input)


class ReturnBehavior(Enum):
    DISPATCH = "dispatch"
    GOTO = "goto"
    ABORT = "abort"
