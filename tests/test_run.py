import pytest
from drive_flow import default_drive, EventInput
from drive_flow.types import ReturnBehavior


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
