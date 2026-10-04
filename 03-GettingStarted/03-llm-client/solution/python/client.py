import asyncio
import sys
from pathlib import Path
import json
import os

from mcp import Client, MCPError, StdioServerParameters
from openai import AsyncOpenAI


def convert_to_llm_tool(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }


async def call_llm(messages: list[str], tools: list[dict]):
    async with AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ["NVIDIA_API_KEY"],
    ) as llm:
        response = await llm.chat.completions.create(
            model="deepseek-ai/deepseek-v4.1-flash",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=1,
            top_p=0.95,
            max_tokens=4096,
            stream=False,
        )

        print("Finish reason:", response.choices[0].finish_reason)
        return response.choices[0].message
    

async def run():
    server_path = Path(__file__).resolve().with_name("server.py")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    async with Client(server_params) as client:
        print("Connected")

        result = await client.list_tools()

        llm_tools = [
            convert_to_llm_tool(tool)
            for tool in result.tools
        ]

        print(json.dumps(llm_tools, indent=2, ensure_ascii=False))

        # prompt = "141에서 20을 빼줘."
        prompt = "141에서 20을 더해줘."

        messages = [
            {
                "role": "system",
                "content": (
                    "계산 요청은 제공된 계산 도구를 사용하세요. "
                    "도구 결과를 받으면 이를 근거로 한국어로 답하세요."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        message = await call_llm(messages, llm_tools)

        if message.tool_calls:
            messages.append(message.model_dump(exclude_none=True))
            for tool_call in message.tool_calls:
                arguments = json.loads(tool_call.function.arguments)

                print("Tool name:", tool_call.function.name)
                print("Arguments:", arguments)

                try:
                    result = await client.call_tool(
                        tool_call.function.name,
                        arguments=arguments,
                    )

                    print("Tool is_error:", result.is_error)
                    print("Tool result:", result.structured_content)

                    tool_output = json.dumps(
                        result.model_dump(mode="json"),
                        ensure_ascii=False,
                    )

                except MCPError as error:
                    tool_output = json.dumps(
                        {"is_error": True, "message": str(error)},
                        ensure_ascii=False,
                    )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output,
                })

            final_message = await call_llm(messages, llm_tools)

            if final_message.tool_calls:
                print("추가 Tool 호출 요청:", final_message.tool_calls)
            else:
                print("Final answer:", final_message.content)

        else:
            print("Tool 호출 요청이 없습니다.")


if __name__ == "__main__":
    asyncio.run(run())