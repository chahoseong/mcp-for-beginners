from time import perf_counter

import requests


started = perf_counter()


with requests.get(
    "http://127.0.0.1:8000/stream",
    stream=True,
    timeout=10,
) as response:
    response.raise_for_status()
    print("Content-Type:", response.headers["Content-Type"])

    for line in response.iter_lines(chunk_size=1):
        if line:
            elapsed = perf_counter() - started
            print(
                f"{elapsed:.2f}s | {line.decode('utf-8')}",
                flush=True,
            )


print(f"{perf_counter() - started:.2f}s | Stream ended")