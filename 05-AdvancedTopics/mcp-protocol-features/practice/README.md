# Request cancellation practice

Python 3.12 and the official MCP SDK 2.3.0 are used in an independent environment.
This is a supplementary, runnable example for the parent lesson's cancellation
and application resource-management sections.

From this directory:

```powershell
uv sync --python 3.12
uv run python client.py --mode normal
uv run python client.py --mode cancel
uv run python client.py --mode timeout
```

The client starts `server.py` as a separate process and communicates over stdio.
Server logs use stderr and are also saved to `runtime/server.log`. The log file
contains the latest run and is overwritten when its server starts. If the
terminal does not show stderr, inspect it after running the client:

```powershell
Get-Content .\runtime\server.log
```

There is no separate server-start command.

The tool processes three items, reports progress, and writes a per-run `.part`
file in `runtime/`. Its synchronous `finally` closes and removes that file.
`server.log` is the retained observation log, not the temporary `.part` file.
`run_id` is an application identifier for the file, not a JSON-RPC request ID.
In cancel mode, the client cancels its call Task after the first progress report.
In timeout mode, `asyncio.wait_for` cancels the call when its 1.5-second deadline
is reached. The client keeps its connection open while observing file removal,
then lists tools again to check that the server still responds.

Compare the Client's outcome, Server's work/cleanup logs, and actual file state.
Combined terminal output can interleave: its line order is not a protocol trace.
The final progress callback may run after the Server has already removed its
temporary file. File observations describe callback time, not notification
generation time.
The helper's five-second observation deadline is a lab guard, not a guarantee
that cleanup will always finish within five seconds in production.

Teaching focus: analyse work interruption and cleanup evidence. Connection,
logging, and observation scaffolding are provided by the tutor. The learner's
earlier `try/finally` correction supplies the cleanup pattern. This example
does not yet introduce cleanup that itself awaits, shared lifespan resources,
or recovery after forced process termination.
