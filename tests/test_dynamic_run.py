import pytest
from drive_flow import default_drive, EventInput
from drive_flow.types import ReturnBehavior, _SpecialEventReturn
from drive_flow.dynamic import goto_events, abort_this


class DeliberateExcepion(Exception):
    pass


def test_special_event_init():
    with pytest.raises(TypeError):
        _SpecialEventReturn("fool", 1)


@pytest.mark.asyncio
async def test_abort():
    @default_drive.make_event
    async def a(event: EventInput, global_ctx):
        assert global_ctx == {"test_ctx": 1}
        return abort_this()

    @default_drive.listen_group([a])
    async def b(event: EventInput, global_ctx):
        assert False, "should not be called"

    result = await default_drive.invoke_event(a, None, {"test_ctx": 1})
    print(result)


@pytest.mark.asyncio
async def test_goto():
    call_a_count = 0

    @default_drive.make_event
    async def a(event: EventInput, global_ctx):
        nonlocal call_a_count
        if call_a_count == 0:
            assert event is None
        elif call_a_count == 1:
            assert event.behavior == ReturnBehavior.GOTO
            assert event.group_name == "$goto"
            assert event.results == {b.id: 2}
            return abort_this()
        else:
            raise ValueError("should not be called more than twice")
        call_a_count += 1
        return 1

    @default_drive.listen_group([a])
    async def b(event: EventInput, global_ctx):
        return goto_events([a], 2)

    @default_drive.listen_group([b])
    async def c(event: EventInput, global_ctx):
        assert False, "should not be called"

    result = await default_drive.invoke_event(a, None, {"test_ctx": 1})
    assert call_a_count == 1
    print(result)
