import asyncio
from datetime import datetime
from drive_events import EventInput, default_drive


@default_drive.make_event
async def start(event: EventInput, global_ctx):
    print("start")


@default_drive.listen_group([start])
async def hello(event: EventInput, global_ctx):
    print(datetime.now(), "hello")
    await asyncio.sleep(0.2)
    print(datetime.now(), "hello done")


@default_drive.listen_group([start])
async def world(event: EventInput, global_ctx):
    print(datetime.now(), "world")
    await asyncio.sleep(0.2)
    print(datetime.now(), "world done")


asyncio.run(default_drive.invoke_event(start))
