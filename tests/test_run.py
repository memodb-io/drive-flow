import asyncio
import pytest
from drive_flow import default_drive, EventInput
from drive_flow.types import ReturnBehavior
from drive_flow.dynamic import abort_this


class DeliberateExcepion(Exception):
    pass


@pytest.mark.asyncio
async def test_simple_order_run():
    @default_drive.make_event
    async def a(event: EventInput, global_ctx):
        assert global_ctx == {"test_ctx": 1}
        return 1

    @default_drive.listen_group([a])
    async def b(event: EventInput, global_ctx):
        assert global_ctx == {"test_ctx": 1}
        assert event.group_name == "0"
        assert event.behavior == ReturnBehavior.DISPATCH
        assert event.results == {a.id: 1}
        return 2

    @default_drive.listen_group([b])
    async def c(event: EventInput, global_ctx):
        assert global_ctx == {"test_ctx": 1}
        assert event.group_name == "0"
        assert event.behavior == ReturnBehavior.DISPATCH
        assert event.results == {b.id: 2}
        return 3

    result = await default_drive.invoke_event(a, None, {"test_ctx": 1})
    print(result)


@pytest.mark.asyncio
async def test_multi_send():
    @default_drive.make_event
    async def a(event: EventInput, global_ctx):
        return 1

    @default_drive.listen_group([a])
    async def b(event: EventInput, global_ctx):
        assert event.group_name == "0"
        assert event.behavior == ReturnBehavior.DISPATCH
        assert event.results == {a.id: 1}
        return 2

    @default_drive.listen_group([a])
    async def c(event: EventInput, global_ctx):
        assert event.group_name == "0"
        assert event.behavior == ReturnBehavior.DISPATCH
        assert event.results == {a.id: 1}
        return 3

    result = await default_drive.invoke_event(a, None, {"test_ctx": 1})
    print(result)


@pytest.mark.asyncio
async def test_multi_recv():
    @default_drive.make_event
    async def start(event: EventInput, global_ctx):
        return None

    @default_drive.listen_group([start])
    async def a(event: EventInput, global_ctx):
        return 1

    @default_drive.listen_group([start])
    async def b(event: EventInput, global_ctx):
        await asyncio.sleep(0.2)
        return 2

    @default_drive.listen_group([a, b])
    async def c(event: EventInput, global_ctx):
        assert event.group_name == "0"
        assert event.behavior == ReturnBehavior.DISPATCH
        assert event.results == {a.id: 1, b.id: 2}
        return 3

    result = await default_drive.invoke_event(start, None, {"test_ctx": 1})
    print(result)


@pytest.mark.asyncio
async def test_multi_recv_cancel():
    @default_drive.make_event
    async def start(event: EventInput, global_ctx):
        return None

    @default_drive.listen_group([start])
    async def a(event: EventInput, global_ctx):
        raise asyncio.CancelledError()
        return 1

    @default_drive.listen_group([start])
    async def b(event: EventInput, global_ctx):
        await asyncio.sleep(0.2)
        return 2

    @default_drive.listen_group([a, b])
    async def c(event: EventInput, global_ctx):
        assert event.group_name == "0"
        assert event.behavior == ReturnBehavior.DISPATCH
        assert event.results == {a.id: 1, b.id: 2}
        return 3

    with pytest.raises(asyncio.CancelledError):
        result = await default_drive.invoke_event(start, None, {"test_ctx": 1})


@pytest.mark.asyncio
async def test_multi_groups():
    @default_drive.make_event
    async def a(event: EventInput, global_ctx):
        return 1

    @default_drive.listen_group([a])
    async def b(event: EventInput, global_ctx):
        return 2

    call_c_count = 0

    @default_drive.listen_group([a])
    @default_drive.listen_group([b, a])
    async def c(event: EventInput, global_ctx):
        nonlocal call_c_count
        if call_c_count == 0:
            assert event.group_name == "1"
            assert event.behavior == ReturnBehavior.DISPATCH
            assert event.results == {a.id: 1}
        elif call_c_count == 1:
            assert event.group_name == "0"
            assert event.behavior == ReturnBehavior.DISPATCH
            assert event.results == {a.id: 1, b.id: 2}
        else:
            assert False, "c should only be called twice"
        call_c_count += 1
        return 3

    result = await default_drive.invoke_event(a, None, {"test_ctx": 1})
    print(result)
    assert call_c_count == 2


@pytest.mark.asyncio
async def test_loop():
    call_a_count = 0

    @default_drive.make_event
    async def a(event: EventInput, global_ctx):
        nonlocal call_a_count
        if call_a_count == 0:
            pass
        elif call_a_count == 1:
            assert event.group_name == "0"
            assert event.behavior == ReturnBehavior.DISPATCH
            assert event.results == {b.id: 2}
            raise DeliberateExcepion()
        call_a_count += 1
        return 1

    @default_drive.listen_group([a])
    async def b(event: EventInput, global_ctx):
        return 2

    a = default_drive.listen_group([b])(a)

    @default_drive.listen_group([a, b])
    async def c(event: EventInput, global_ctx):
        return 3

    with pytest.raises(DeliberateExcepion):
        await default_drive.invoke_event(a, None, {"test_ctx": 1})
    assert call_a_count == 1


@pytest.mark.asyncio
async def test_duplicate_events_not_send():
    call_a_count = 0

    @default_drive.make_event
    async def start(event: EventInput, global_ctx):
        pass

    @default_drive.listen_group([start])
    async def a(event: EventInput, global_ctx):
        nonlocal call_a_count
        if call_a_count <= 1:
            pass
        elif call_a_count == 2:
            return abort_this()
        call_a_count += 1
        return 1

    a = default_drive.listen_group([a])(a)  # self loop

    @default_drive.listen_group([start])
    async def b(event: EventInput, global_ctx):
        return 2

    call_c_count = 0

    @default_drive.listen_group([a, b])
    async def c(event: EventInput, global_ctx):
        nonlocal call_c_count
        assert call_c_count < 1, "c should only be called once"
        call_c_count += 1
        print("Call C")
        return 3

    r = await default_drive.invoke_event(start, None, {"test_ctx": 1})
    assert call_a_count == 2
    assert call_c_count == 1
    print({default_drive.get_event_from_id(k).repr_name: v for k, v in r.items()})
