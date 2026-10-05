import asyncio
from time import perf_counter

from mcp import Client


async def main() -> None:
    async with Client(
        "http://127.0.0.1:8000/mcp",
        mode="2026-07-28",
    ) as client:
        print("Connected")

        tools = await client.list_tools()
        for tool in tools.tools:
            print("Tool:", tool.name)

        started = perf_counter()

        async def show_progress(
            progress:float,
            total: float | None,
            message: str | None,
        ) -> None:
            elapsed = perf_counter() - started
            print(
                f"{elapsed:.2f}s | Progress: {progress}/{total} | {message}",
                flush=True,
            )

        result = await client.call_tool(
            "process_files",
            arguments={
                "files": ["lecture.txt", "memo.txt"]
            },
            progress_callback=show_progress,
        )

        elapsed = perf_counter() - started
        print(f"{elapsed:.2f}s | Final result")
        print("is_error:", result.is_error)
        print("structured_content:", result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())