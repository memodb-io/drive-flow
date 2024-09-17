from copy import copy
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Optional, Union, Callable, TypedDict, Literal

from .utils import (
    string_to_md5_hash,
    generate_uuid,
    function_or_method_to_string,
    function_or_method_to_repr,
)


class ReturnBehavior(Enum):
    DISPATCH = "dispatch"
    GOTO = "goto"
    ABORT = "abort"
    INPUT = "input"


class TaskStatus(Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class InvokeInterCache(TypedDict):
    result: Any
    already_sent_to_event_group: set[str]


GroupEventReturns = dict[str, Any]


@dataclass
class EventGroupInput:
    group_name: str
    results: GroupEventReturns
    behavior: ReturnBehavior = ReturnBehavior.DISPATCH


@dataclass
class EventInput(EventGroupInput):
    task_id: str = field(default_factory=generate_uuid)

    @classmethod
    def from_input(cls: "EventInput", input_data: dict[str, Any]) -> "EventInput":
        return cls(
            group_name="user_input", results=input_data, behavior=ReturnBehavior.INPUT
        )


@dataclass
class _SpecialEventReturn:
    behavior: ReturnBehavior
    returns: Any

    def __post_init__(self):
        if not isinstance(self.behavior, ReturnBehavior):
            raise TypeError(
                f"behavior must be a ReturnBehavior, not {type(self.behavior)}"
            )


# (group_event_results, global ctx set by user) -> result
EventFunction = Callable[
    [Optional[EventInput], Optional[Any]], Awaitable[Union[Any, _SpecialEventReturn]]
]


@dataclass
class EventGroup:
    name: str
    events_hash: str
    events: dict[str, "BaseEvent"]
    retrigger_type: Literal["all", "any"] = "all"

    def hash(self) -> str:
        return self.events_hash


class BaseEvent:
    parent_groups: dict[str, EventGroup]
    func_inst: EventFunction
    id: str
    repr_name: str

    def __init__(
        self,
        func_inst: EventFunction,
        parent_groups: Optional[dict[str, EventGroup]] = None,
    ):
        self.parent_groups = parent_groups or {}
        self.func_inst = func_inst
        self.id = string_to_md5_hash(function_or_method_to_string(self.func_inst))
        self.repr_name = function_or_method_to_repr(self.func_inst)
        self.meta = {"func_body": function_or_method_to_string(self.func_inst)}

    def debug_string(self, exclude_events: Optional[set[str]] = None) -> str:
        exclude_events = exclude_events or set([self.id])
        parents_str = format_parents(self.parent_groups, exclude_events=exclude_events)
        return f"{self.repr_name}\n{parents_str}"

    def __repr__(self) -> str:
        return f"Node(source={self.repr_name})"

    async def solo_run(
        self, event_input: EventInput, global_ctx: Any = None
    ) -> Awaitable[Any]:
        return await self.func_inst(event_input, global_ctx)


@dataclass
class Task:
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    upated_at: datetime = field(default_factory=datetime.now)


def format_parents(parents: dict[str, EventGroup], exclude_events: set[str], indent=""):
    # Below code is ugly
    # But it works and only for debug display
    result = []
    for i, parent_group in enumerate(parents.values()):
        is_last_group = i == len(parents) - 1
        group_prefix = "└─ " if is_last_group else "├─ "
        result.append(indent + group_prefix + f"<{parent_group.name}>")
        for j, parent in enumerate(parent_group.events.values()):
            root_events = copy(exclude_events)
            is_last = j == len(parent_group.events) - 1
            child_indent = indent + ("    " if is_last_group else "│   ")
            inter_indent = "   " if is_last else "│  "
            prefix = "└─ " if is_last else "├─ "
            if parent.id in root_events:
                result.append(f"{child_indent}{prefix}{parent.repr_name} <loop>")
                continue
            root_events.add(parent.id)
            parent_debug = parent.debug_string(exclude_events=root_events).split("\n")
            parent_debug = [p for p in parent_debug if p.strip()]
            result.append(f"{child_indent}{prefix}{parent.repr_name}")
            for line in parent_debug[1:]:
                result.append(f"{child_indent}{inter_indent}{line}")
    return "\n".join(result)
