import inspect
from typing import Callable
from .types import BaseEvent, EventFunction


class EventEngineCls:
    def __init__(self):
        self.__function_maps: dict[str, EventFunction] = {}
        self.__event_maps: dict[str, BaseEvent] = {}

    def reset(self):
        self.__function_maps = {}
        self.__event_maps = {}

    def listen_groups(
        self, group_markers: list[BaseEvent], group_name: str = None
    ) -> Callable[[BaseEvent], BaseEvent]:
        assert all(
            [isinstance(m, BaseEvent) for m in group_markers]
        ), "group_markers must be a list of BaseEvent"
        group_markers = list(set(group_markers))

        def decorator(func: BaseEvent) -> BaseEvent:
            if not isinstance(func, BaseEvent):
                func = self.make_event(func)
            this_group_name = group_name or f"{len(func.parent_groups)}"
            func.parent_groups.append((this_group_name, group_markers))
            return func

        return decorator

    def goto(self, group_markers: list[BaseEvent], *args):
        pass

    def make_event(self, func: EventFunction) -> BaseEvent:
        if isinstance(func, BaseEvent):
            return func
        assert inspect.iscoroutinefunction(
            func
        ), "Event function must be a coroutine function"
        event = BaseEvent(func)
        self.__function_maps[event.id] = func
        self.__event_maps[event.id] = event
        return event
