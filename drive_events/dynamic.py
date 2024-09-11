from typing import Any
from .types import (
    BaseEvent,
    _SpecialEventReturn,
    ReturnBehavior,
)


def goto_events(
    group_markers: list[BaseEvent], any_return: Any = None
) -> _SpecialEventReturn:
    return _SpecialEventReturn(
        behavior=ReturnBehavior.GOTO, returns=(group_markers, any_return)
    )


def abort_this():
    return _SpecialEventReturn(behavior=ReturnBehavior.ABORT, returns=None)
