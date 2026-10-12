"""Observe a normal call, explicit cancellation, or a client deadline."""

import argparse
import asyncio
from contextlib import suppress
from pathlib import Path
import sys
from uuid import uuid4

from mcp import Client
from mcp.client.stdio import StdioServerParameters

practice_dir = Path(__file__).resolve().parent


async def wait_for_cleanup(temporary_file: Path) -> None:
    """Keep the stdio connection open while observing server-side cleanup."""
    deadline = asyncio.get_running_loop().time() + 5
    while temporary_file.exists():
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("Temporary file still exists after waiting for cleanup")
        await asyncio.sleep(0.05)


async def main(mode: str) -> None:
    run_id = uuid4().hex
    temporary_file = practice_dir / "runtime" / f"{run_id}.part"
    first_progress = asyncio.Event()

    async def show_progress(progress: float, total: float | None, message: str | None) -> None:
        print(f"CLIENT | Progress: {progress}/{total} | {message}", flush=True)
        print(f"CLIENT | Temporary file exists at this observation: {temporary_file.exists()}", flush=True)
        first_progress.set()

    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(practice_dir / "server.py")],
        cwd=str(practice_dir),
    )
    async with Client(parameters) as client:
        print(f"CLIENT | Connected | Protocol: {client.protocol_version}", flush=True)
        tools = await client.list_tools()
        print(f"CLIENT | Tools: {[tool.name for tool in tools.tools]}", flush=True)
        print(f"CLIENT | Mode: {mode}", flush=True)
        task = asyncio.create_task(
            client.call_tool(
                "process_items",
                {"items": ["alpha", "beta", "gamma"], "run_id": run_id},
                progress_callback=show_progress,
            )
        )

        if mode == "cancel":
            # Wait for evidence that this request is running before cancelling it.
            progress_waiter = asyncio.create_task(first_progress.wait())
            try:
                done, _ = await asyncio.wait(
                    [task, progress_waiter],
                    timeout=5,
                    return_when=asyncio.FIRST_COMPLETED,
                )
            finally:
                if not progress_waiter.done():
                    progress_waiter.cancel()
                with suppress(asyncio.CancelledError):
                    await progress_waiter
            if task in done:
                result = await task
                raise RuntimeError(f"Call finished before the cancellation point: {result}")
            if not first_progress.is_set():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                raise TimeoutError("No progress received before the cancellation point")
            print("CLIENT | Requesting cancellation", flush=True)
            task.cancel()

        try:
            if mode == "timeout":
                result = await asyncio.wait_for(task, timeout=1.5)
            else:
                result = await task
            print(f"CLIENT | Tool is_error: {result.is_error}", flush=True)
            print(f"CLIENT | Tool result: {result.structured_content}", flush=True)
            if result.is_error:
                raise RuntimeError(f"Tool failed: {result.content}")
        except asyncio.CancelledError:
            print("CLIENT | Local call task cancelled", flush=True)
        except TimeoutError:
            print("CLIENT | Call deadline reached", flush=True)

        await wait_for_cleanup(temporary_file)
        print(f"CLIENT | Temporary file exists after cleanup: {temporary_file.exists()}", flush=True)
        tools = await client.list_tools()
        print(f"CLIENT | Server still responds: {any(tool.name == 'process_items' for tool in tools.tools)}", flush=True)

    print(f"CLIENT | Server log saved to: {practice_dir / 'runtime' / 'server.log'}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["normal", "cancel", "timeout"], default="normal")
    asyncio.run(main(parser.parse_args().mode))
