import asyncio
from openai import AsyncOpenAI
from drive_flow import default_drive, EventInput, ReturnBehavior
from drive_flow.dynamic import goto_events, abort_this

openai_client = AsyncOpenAI()


@default_drive.make_event
async def plan(event: EventInput, global_ctx):
    print("Planning")
    if event.behavior == ReturnBehavior.INPUT:
        query = event.results["query"]
        global_ctx["user_query"] = query


@default_drive.listen_group([plan])
async def action(event: EventInput, global_ctx):
    print("Executing")


@default_drive.listen_group([action])
async def observate(event: EventInput, global_ctx):
    print("Observing")


# make it a loop
plan = default_drive.listen_group([observate])(plan)

if __name__ == "__main__":
    question = "What is the answer to the ultimate question of life, the universe, and everything?"
    storage_results = {}
    print(observate.debug_string())
    # asyncio.run(
    #     default_drive.invoke_event(
    #         plan,
    #         event_input=EventInput.from_input({"query": question}),
    #         global_ctx=storage_results,
    #     )
    # )

    # if "answer" not in storage_results:
    #     print(f"Failed to get answer {question}")
    #     exit(1)
    # print(storage_results)
