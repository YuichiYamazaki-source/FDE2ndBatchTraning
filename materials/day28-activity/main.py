import json
from openai import OpenAI
from dotenv import load_dotenv
from weather import get_weather, find_hottest_city
import os

load_dotenv(dotenv_path="../../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_hottest_city",
            "description": "Find the hottest city among all available cities",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def call_function(name, args):
    if name == "get_weather":
        return get_weather(args["city"])
    elif name == "find_hottest_city":
        city, temp = find_hottest_city()
        return {"city": city, "temp": temp}


SYSTEM_PROMPT = (
    "You are a friendly weather assistant. "
    "Answer in a short and friendly format not exceeding 10 words. "
    "If the tool returns 'City not found in the database.' or any error, "
    "respond with: 'I am unaware of this city.' Do not make up weather data."
)


def agent(query: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # No tool call — return direct answer
    if not message.tool_calls:
        return message.content

    # Execute each tool call
    messages.append(message)
    for tool_call in message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        result = call_function(name, args)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })

    # Final response with tool results
    final = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return final.choices[0].message.content


if __name__ == "__main__":
    queries = [
        "What is the weather in Chennai?",
        "Which is the hottest city?",
        "weather in Delhi",
        "What about London?",
        "Give me the weather update for ayush.",
    ]

    for q in queries:
        print(f"Q: {q}")
        print(f"A: {agent(q)}\n")
