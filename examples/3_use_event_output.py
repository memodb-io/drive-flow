import asyncio
from datetime import datetime
from drive_events import EventInput, default_drive


@default_drive.make_event
async def start(event: EventInput, global_ctx):
    print("start")


@default_drive.listen_groups([start])
async def hello(event: EventInput, global_ctx):
    return 1


@default_drive.listen_groups([start])
async def world(event: EventInput, global_ctx):
    return 2


@default_drive.listen_groups([hello, world])
async def adding(event: EventInput, global_ctx):
    results = event.results
    print("adding", hello, world)
    return results[hello.id] + results[world.id]


results = asyncio.run(default_drive.invoke_event(start))
assert results[adding.id] == 3
