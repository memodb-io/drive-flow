import asyncio
from datetime import datetime
from drive_events import default_drive, EventInput
from drive_events.dynamic import goto_events


@default_drive.make_event
async def tick(event: EventInput, global_ctx):
    await asyncio.sleep(1)
    return "tick"


@default_drive.listen_group([tick])
async def tok(event: EventInput, global_ctx):
    print(datetime.now(), f"{event.results[tick.id]}, then tok")
    return goto_events([tick])


asyncio.run(default_drive.invoke_event(tick))
