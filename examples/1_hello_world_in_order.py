import asyncio
from drive_events import EventInput, default_drive


@default_drive.make_event
async def hello(event: EventInput, global_ctx):
    print("hello")


@default_drive.listen_group([hello])
async def world(event: EventInput, global_ctx):
    print("world")


asyncio.run(default_drive.invoke_event(hello))
