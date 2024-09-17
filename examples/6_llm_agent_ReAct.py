import asyncio
import json
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageToolCall
from drive_flow import default_drive, EventInput, ReturnBehavior
from drive_flow.dynamic import goto_events, abort_this

openai_client = AsyncOpenAI()
use_model = "gpt-4o-mini"


def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


function_describe = [
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two integers and returns the result integer",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "The first integer to multiply.",
                    },
                    "b": {
                        "type": "integer",
                        "description": "The second integer to multiply.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two integers and returns the result integer",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "The first integer to add.",
                    },
                    "b": {
                        "type": "integer",
                        "description": "The second integer to add.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
]


@default_drive.make_event
async def plan(event: EventInput, global_ctx):
    print("Planning...")
    if event.behavior == ReturnBehavior.INPUT:
        query = event.results["query"]
        messages = [
            {
                "role": "system",
                "content": "You are a assistant. Use the following functions: multiply, add to compute the result of a calculation. Compute the result step by step",
            },
            {
                "role": "user",
                "content": query,
            },
        ]
        global_ctx["messages"] = messages
    messages = global_ctx["messages"]
    response = await openai_client.chat.completions.create(
        messages=messages,
        model=use_model,
        tools=function_describe,
    )
    if response.choices[0].finish_reason == "tool_calls":
        return response.choices[0].message
    else:
        global_ctx["answer"] = response.choices[0].message.content
        return abort_this()


@default_drive.listen_group([plan])
async def action(event: EventInput, global_ctx):
    func_calls: list[ChatCompletionMessageToolCall] = event.results[plan.id].tool_calls
    print(
        "Executing",
        [c.function.name for c in func_calls],
        "with arguments",
        [json.loads(c.function.arguments) for c in func_calls],
    )
    results = []
    for func_c in func_calls:
        if func_c.function.name == "multiply":
            result = multiply(**json.loads(func_c.function.arguments))
        elif func_c.function.name == "add":
            result = add(**json.loads(func_c.function.arguments))
        else:
            raise ValueError(f"Unknown function {func_c.function.name}")
        results.append(result)
    return event.results[plan.id], func_calls, results


@default_drive.listen_group([action])
async def observate(event: EventInput, global_ctx):
    func_calls: list[ChatCompletionMessageToolCall]
    tool_call_response, func_calls, func_results = event.results[action.id]
    print("Observing", [c.function.name for c in func_calls])
    messages = global_ctx["messages"]
    messages.append(tool_call_response)
    messages.extend(
        [
            {"role": "tool", "content": json.dumps({"result": r}), "tool_call_id": c.id}
            for c, r in zip(func_calls, func_results)
        ]
    )
    return goto_events([plan])


if __name__ == "__main__":
    question = "3+3*2+20*4"
    storage_results = {}
    print(observate.debug_string())
    asyncio.run(
        default_drive.invoke_event(
            plan,
            event_input=EventInput.from_input({"query": question}),
            global_ctx=storage_results,
        )
    )

    if "answer" not in storage_results:
        print(f"Failed to get answer {question}")
        exit(1)
    print(storage_results["answer"])
