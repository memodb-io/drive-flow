from typing import Any
from .types import BaseEvent, EventInput, Task, GroupEventReturns
from .utils import generate_uuid


class BaseBroker:
    async def append(self, event: BaseEvent, event_input: EventInput) -> Task:
        raise NotImplementedError()

    async def callback_after_run_done(self) -> tuple[BaseEvent, Any]:
        raise NotImplementedError()
