<div align="center">
  <h1>drive-flow</h1>
  <p><strong>Build event-driven workflows with python async functions</strong></p>
  <p>
    <a href="https://pypi.org/project/drive-flow/" > 
    	<img src="https://img.shields.io/badge/python->=3.9.11-blue">
    </a>
    <a href="https://codecov.io/github/memodb-io/drive-flow" > 
     <img src="https://codecov.io/github/memodb-io/drive-flow/graph/badge.svg?token=T1Q1JB1NGM"/> 
	 </a>
    <a href="https://pypi.org/project/drive-flow/">
      <img src="https://img.shields.io/pypi/v/drive-flow.svg">
    </a>
  </p>
</div>


🌬️ [Zero dependency](./requirements.txt). No trouble, no loss.

🍰 With **intuitive decorators**, write your async workflow like a piece of cake. 

🔄 Support dynamic dispatch(`goto`, `abort`). Create a **looping or if-else workflow with ease**. 

🔜 **Fully asynchronous**. Events are always triggered at the same time if they listen to the same group!





## Install

**Install from PyPi**

```shell
pip install drive-flow
```

**Install from source**

```shell
# clone this repo first
cd drive-flow
pip install -e .
```



## Quick Start

A hello world example:

```python
import asyncio
from drive_flow import EventInput, default_drive


@default_drive.make_event
async def hello(event: EventInput, global_ctx):
    print("hello")

@default_drive.listen_group([hello])
async def world(event: EventInput, global_ctx):
    print("world")

# display the dependencies of 'world' event
print(world.debug_string()) 
asyncio.run(default_drive.invoke_event(hello))
```

In this example, The return of `hello` event will trigger `world` event.

> [!TIP]
>
> Hello world is not cool enough? Try to build a [ReAct Agent Workflow](./examples/6_llm_agent_ReAct.py) with `drive-flow`

### Break-down

To make an event function, there are few elements:

* Input Signature: must be `(event: EventInput, global_ctx)`. `EventInput` is the returns of the listening groups. `global_ctx` is set by you when invoking events, it can be anything and default to `None`.

  This [example](./examples/3_use_event_output.py) shows how to get returns from `EventInput` .
* Make sure you decorate the function with `@default_drive.make_event` or `@default_drive.listen_group([EVENT,...])`

Then, run your workflow from any event:

```python
await default_drive.invoke_event(EVENT, EVENT_INPUT, GLOBAL_CTX)
```

Check out [examples](./examples) for more detailed usages and features!

## Features

### Multi-Recv

`drive_flow` allow an event to be triggered only when a group of events are produced:

<details>
<summary> code snippet</summary>

```python
@default_drive.make_event
async def start(event: EventInput, global_ctx):
    print("start")
    
@default_drive.listen_group([start])
async def hello(event: EventInput, global_ctx):
    return 1


@default_drive.listen_group([start])
async def world(event: EventInput, global_ctx):
    return 2


@default_drive.listen_group([hello, world])
async def adding(event: EventInput, global_ctx):
    results = event.results
    print("adding", hello, world)
    return results[hello.id] + results[world.id]


results = asyncio.run(default_drive.invoke_event(start))
assert results[adding.id] == 3
```

`adding` will be triggered at first time as long as `hello` and `world` are done.
</details>

#### Re-trigger the event

`drive_flow` suppports different behaviors for multi-event retriggering:

- `all`: retrigger this event only when all the listening events are updated.
- `any`: retrigger this event as long as one of the listening events is updated.

Check out this [example](./examples/5_retrigger_type.py) for more details

### Parallel

`drive_flow` is perfect for workflows that have many network IO that can be awaited in parallel. If two events are listened to the same group of events, then they will be triggered at the same time:

<details>
<summary> code snippet</summary>

```python
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
```

</details>



### Dynamic

`drive_flow` is dynamic. You can use `goto` and `abort` to change the workflow at runtime:

<details>
<summary> code snippet for abort_this</summary>

```python
from drive_flow.dynamic import abort_this

@default_drive.make_event
async def a(event: EventInput, global_ctx):
    return abort_this()
# abort_this is not exiting the whole workflow,
# only abort this event's return and not causing any other influence
# `a` chooses to abort its return. So no more events in this invoking.
# this invoking then will end
@default_drive.listen_group([a])
async def b(event: EventInput, global_ctx):
    assert False, "should not be called"
    
asyncio.run(default_drive.invoke_event(a))
```

</details>

<details>
<summary> code snippet for goto</summary>

```python
from drive_flow.types import ReturnBehavior
from drive_flow.dynamic import goto_events, abort_this

call_a_count = 0
@default_drive.make_event
async def a(event: EventInput, global_ctx):
    global call_a_count
    if call_a_count == 0:
        assert event is None
    elif call_a_count == 1:
        assert event.behavior == ReturnBehavior.GOTO
        assert event.results == {b.id: 2}
        return abort_this()
    call_a_count += 1
    return 1

@default_drive.listen_group([a])
async def b(event: EventInput, global_ctx):
    return goto_events([a], 2)

@default_drive.listen_group([b])
async def c(event: EventInput, global_ctx):
    assert False, "should not be called"
    
asyncio.run(default_drive.invoke_event(a))
```

</details>



## TODO

- [x] fix: streaming event executation
- [x] fix: an event never receive the listened events' results twice (de-duplication), unless the group is totally updated for `retrigger_type='all'`
- [x] Add ReAct workflow example
