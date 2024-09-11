import inspect
import asyncio
from typing import Callable, Optional, Union, Any, Tuple
from .types import (
    BaseEvent,
    EventFunction,
    EventGroup,
    EventInput,
    _SpecialEventReturn,
    ReturnBehavior,
)
from .broker import BaseBroker
from .utils import (
    logger,
    string_to_md5_hash,
)


class EventEngineCls:
    def __init__(self, name="default", broker: Optional[BaseBroker] = None):
        self.name = name
        self.broker = broker or BaseBroker()
        self.__event_maps: dict[str, BaseEvent] = {}
        self.__max_group_size = 0

    def reset(self):
        self.__event_maps = {}

    def get_event_from_id(self, event_id: str) -> Optional[BaseEvent]:
        return self.__event_maps.get(event_id)

    def make_event(self, func: Union[EventFunction, BaseEvent]) -> BaseEvent:
        if isinstance(func, BaseEvent):
            self.__event_maps[func.id] = func
            return func
        assert inspect.iscoroutinefunction(
            func
        ), "Event function must be a coroutine function"
        event = BaseEvent(func)
        self.__event_maps[event.id] = event
        return event

    def listen_group(
        self, group_markers: list[BaseEvent], group_name: Optional[str] = None
    ) -> Callable[[BaseEvent], BaseEvent]:
        assert all(
            [isinstance(m, BaseEvent) for m in group_markers]
        ), "group_markers must be a list of BaseEvent"
        assert all(
            [m.id in self.__event_maps for m in group_markers]
        ), f"group_markers must be registered in the same event engine, current event engine is {self.name}"
        group_markers_in_dict = {event.id: event for event in group_markers}

        def decorator(func: BaseEvent) -> BaseEvent:
            if not isinstance(func, BaseEvent):
                func = self.make_event(func)
            assert (
                func.id in self.__event_maps
            ), f"Event function must be registered in the same event engine, current event engine is {self.name}"
            this_group_name = group_name or f"{len(func.parent_groups)}"
            this_group_hash = string_to_md5_hash(":".join(group_markers_in_dict.keys()))
            new_group = EventGroup(
                this_group_name, this_group_hash, group_markers_in_dict
            )
            self.__max_group_size = max(
                self.__max_group_size, len(group_markers_in_dict)
            )
            if new_group.hash() in func.parent_groups:
                logger.warning(f"Group {group_markers} already listened by {func}")
                return func
            func.parent_groups[new_group.hash()] = new_group
            return func

        return decorator

    def goto(self, group_markers: list[BaseEvent], *args):
        raise NotImplementedError()

    async def invoke_event(
        self,
        event: BaseEvent,
        event_input: Optional[EventInput] = None,
        global_ctx: Any = None,
        max_async_events: Optional[int] = None,
    ) -> dict[str, Any]:
        this_run_ctx = {}
        queue: list[Tuple[BaseEvent, EventInput]] = [(event, event_input)]

        async def run_event(current_event: BaseEvent, current_event_input: Any):
            result = await current_event.solo_run(current_event_input, global_ctx)
            this_run_ctx[current_event.id] = result
            if isinstance(result, _SpecialEventReturn):
                if result.behavior == ReturnBehavior.GOTO:
                    group_markers, any_return = result.returns
                    for group_marker in group_markers:
                        this_group_returns = {current_event.id: any_return}
                        build_input_goto = EventInput(
                            group_name="$goto",
                            results=this_group_returns,
                            behavior=ReturnBehavior.GOTO,
                        )
                        queue.append((group_marker, build_input_goto))
                elif result.behavior == ReturnBehavior.ABORT:
                    return
            else:
                # dispath to events who listen
                for cand_event in self.__event_maps.values():
                    cand_event_parents = cand_event.parent_groups
                    for group_hash, group in cand_event_parents.items():
                        if current_event.id in group.events and all(
                            [event_id in this_run_ctx for event_id in group.events]
                        ):
                            this_group_returns = {
                                event_id: this_run_ctx[event_id]
                                for event_id in group.events
                            }
                            build_input = EventInput(
                                group_name=group.name, results=this_group_returns
                            )
                            queue.append((cand_event, build_input))

        while len(queue):
            this_batch_events = queue[:max_async_events] if max_async_events else queue
            queue = queue[max_async_events:] if max_async_events else []
            logger.debug(
                f"Running a turn with {len(this_batch_events)} event tasks, left {len(queue)} event tasks in queue"
            )
            await asyncio.gather(
                *[run_event(*run_event_input) for run_event_input in this_batch_events]
            )
        return this_run_ctx
