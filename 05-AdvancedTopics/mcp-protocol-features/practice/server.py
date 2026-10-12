"""A single async tool for observing work cancellation over stdio."""

import asyncio
import logging
from pathlib import Path
import sys
from uuid import UUID

from mcp.server import MCPServer
from mcp.server.mcpserver import Context

runtime_dir = Path(__file__).resolve().parent / "runtime"
runtime_dir.mkdir(exist_ok=True)

logger = logging.getLogger("cancellation_practice")
logger.setLevel(logging.INFO)
logger.propagate = False
formatter = logging.Formatter("SERVER | %(message)s")

# Persist the server's observations even when the terminal does not show stderr.
file_handler = logging.FileHandler(runtime_dir / "server.log", mode="w", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)

mcp = MCPServer("cancellation-practice")


@mcp.tool()
async def process_items(items: list[str], run_id: str, ctx: Context) -> int:
    """Process items with progress updates, cleaning up the temporary file."""
    # This application ID gives each run its own file; it is not a JSON-RPC ID.
    run_key = UUID(run_id).hex
    runtime_dir.mkdir(exist_ok=True)
    temporary_file = runtime_dir / f"{run_key}.part"
    file = temporary_file.open("w", encoding="utf-8")
    logger.info("Work started; temporary file opened")

    try:
        for completed, item in enumerate(items, start=1):
            await asyncio.sleep(1)
            file.write(f"{item}\n")
            file.flush()
            logger.info("Processed %s/%s: %s", completed, len(items), item)
            await ctx.report_progress(completed, total=len(items), message=item)
        logger.info("Work completed")
        return len(items)
    except asyncio.CancelledError:
        logger.info("Work interrupted by cancellation")
        raise
    finally:
        logger.info("Cleanup started")
        file.close()
        temporary_file.unlink()
        logger.info("Cleanup completed; file.closed=%s", file.closed)


if __name__ == "__main__":
    mcp.run(transport="stdio")
