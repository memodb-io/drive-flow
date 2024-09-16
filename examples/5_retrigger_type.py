import asyncio
from drive_flow import default_drive, EventInput
from drive_flow.dynamic import goto_events


@default_drive.make_event
async def on_start(event: EventInput, global_ctx):
    print("---------New_turn---------")


@default_drive.listen_group([on_start])
async def a(event: EventInput, global_ctx):
    await asyncio.sleep(0.1)
    print("a")


@default_drive.listen_group([on_start])
async def b(event: EventInput, global_ctx):
    await asyncio.sleep(0.5)
    print("b")


@default_drive.listen_group([a, b], retrigger_type="any")
async def c(event: EventInput, global_ctx):
    print("C is triggered")


# default retrigger_type is 'all'
@default_drive.listen_group([a, b], retrigger_type="all")
async def d(event: EventInput, global_ctx):
    print("D is triggered")
    return goto_events([on_start])  # re-loop the workflow


if __name__ == "__main__":
    asyncio.run(default_drive.invoke_event(on_start))

# For the first turn, the print will be:
# ---------New_turn---------
# a
# b
# C is triggered
# D is triggered

# But for the rest of the turns, the print will be:
# ---------New_turn---------
# a
# C is triggered
# b
# C is triggered
# D is triggered

# Because the retrigger_type of d is 'all', it will be triggered only when all the events in the group (a, b) are updated.
# The retrigger_type of c is 'any'. So when a is updated, it will trigger c, and when b is updated, it will trigger c again.
