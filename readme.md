<div align="center">
  <h1>drive-events</h1>
  <p><strong>Build event-driven workflows with python async functions</strong></p>
  <p>
    <a href="https://pypi.org/project/drive-events/" > 
    	<img src="https://img.shields.io/badge/python->=3.9.11-blue">
    </a>
    <a href="https://codecov.io/github/memodb-io/drive-events" > 
     <img src="https://codecov.io/github/memodb-io/drive-events/graph/badge.svg?token=T1Q1JB1NGM"/> 
	 </a>
    <a href="https://pypi.org/project/drive-events/">
      <img src="https://img.shields.io/pypi/v/drive-events.svg">
    </a>
  </p>
</div>








## Install

**Install from PyPi**

```shell
pip install drive-events
```

**Install from source**

```shell
# clone this repo first
cd drive-events
pip install -e .
```

## Quick Start

A hello world example:

```python
import asyncio
from drive_events import EventInput, default_drive


@default_drive.make_event
async def hello(event: EventInput, global_ctx):
    print("hello")


@default_drive.listen_groups([hello])
async def world(event: EventInput, global_ctx):
    print("world")

asyncio.run(default_drive.invoke_event(hello))
```

In this example, The return of `hello` event will trigger `world` event.

To make an event function, there are few elements:

* Input Signature: must be `(event: EventInput, global_ctx)`
  * `EventInput` is the returns of the listening groups.
  * `global_ctx` is set by you when invoking events, it can be anything and default to `None`
* Make sure you decorate the function with `@default_drive.make_event` or `@default_drive.listen_groups([EVENT,...])`

Then, run your workflow from any event:

```python
await default_drive.invoke_event(EVENT, EVENT_INPUT, GLOBAL_CTX)
```

Check out [examples](./examples) for more user cases!



