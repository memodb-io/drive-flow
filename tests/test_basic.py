import pytest

from drive_events import default_drive, EventInput


@pytest.mark.asyncio
async def test_order():
    @default_drive.make_event
    async def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    async def b(event: EventInput):
        return 2

    @default_drive.listen_groups([b])
    async def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())

    assert await a.solo_run(None) == 1
    assert await b.solo_run(None) == 2
    assert await c.solo_run(None) == 3


@pytest.mark.asyncio
async def test_multi_send():
    @default_drive.make_event
    async def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    async def b(event: EventInput):
        return 2

    @default_drive.listen_groups([a])
    async def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())
    assert await a.solo_run(None) == 1
    assert await b.solo_run(None) == 2
    assert await c.solo_run(None) == 3


@pytest.mark.asyncio
async def test_multi_recv():
    @default_drive.make_event
    async def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    async def a1(event: EventInput):
        return 1

    @default_drive.make_event
    async def b(event: EventInput):
        return 2

    @default_drive.listen_groups([a1, b])
    async def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())
    assert await a.solo_run(None) == 1
    assert await b.solo_run(None) == 2
    assert await c.solo_run(None) == 3


@pytest.mark.asyncio
async def test_loop():
    @default_drive.make_event
    async def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    async def b(event: EventInput):
        return 2

    a = default_drive.listen_groups([b])(a)

    @default_drive.listen_groups([a, b])
    async def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())

    assert await a.solo_run(None) == 1
    assert await b.solo_run(None) == 2
    assert await c.solo_run(None) == 3
