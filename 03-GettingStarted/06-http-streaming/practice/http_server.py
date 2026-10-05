import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse


app = FastAPI()


async def event_stream():
    for i in range(1, 6):
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(1)


@app.get("/stream")
async def stream():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)