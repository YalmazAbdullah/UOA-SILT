import asyncio
import json
import sys
import websockets

BASE_WS_URL = "ws://localhost:8000/ws/logs"


async def async_input(prompt: str) -> str:
    """Non-blocking reader for standard input."""
    print(prompt, end="", flush=True)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sys.stdin.readline)


async def session_input_loop(session_queue: asyncio.Queue):
    """Continuously prompts the user for a new session_id."""
    while True:
        line = await async_input("\n[Enter new session_id to switch]: ")
        new_session = line.strip()
        if new_session:
            await session_queue.put(new_session)


async def connection_manager(initial_session: str, session_queue: asyncio.Queue):
    """Manages connection lifecycle and cancels the current connection when a new session_id arrives."""
    current_session = initial_session

    while True:
        url = f"{BASE_WS_URL}/{current_session}"
        print(f"\n---> Connecting to session: {current_session}")

        # Start listening task for current session
        listen_task = asyncio.create_task(listen_ws(url, current_session))
        # Task that waits for user input from queue
        switch_task = asyncio.create_task(session_queue.get())

        # Wait for either a disconnect/error in listening OR new user input
        done, pending = await asyncio.wait(
            [listen_task, switch_task], return_when=asyncio.FIRST_COMPLETED
        )

        if switch_task in done:
            # User typed a new session ID
            current_session = switch_task.result()
            print(f"---> Switching session to {current_session}...")
            listen_task.cancel()
            try:
                await listen_task
            except asyncio.CancelledError:
                pass
        else:
            # Connection dropped or closed
            switch_task.cancel()
            print("---> Reconnecting in 3 seconds...")
            await asyncio.sleep(3)


async def listen_ws(url: str, session_id: str):
    """Handles receiving messages for a specific active WebSocket connection."""
    try:
        async with websockets.connect(url) as websocket:
            print(f"---> Active stream connected for [{session_id}]")
            async for message in websocket:
                log_data = json.loads(message)
                sys.stdout.write(
                    f"\n[LOG RECEIVED - {session_id}] {json.dumps(log_data, indent=2)}\n"
                )
                sys.stdout.flush()
    except asyncio.CancelledError:
        print(f"---> Cleanly disconnected from [{session_id}]")
        raise
    except Exception as e:
        print(f"\n---> Error on session [{session_id}]: {e}")


async def main():
    initial_session = (
        sys.argv[1] if len(sys.argv) > 1 else "123e4567-e89b-12d3-a456-426614174000"
    )

    session_queue = asyncio.Queue()

    # Run the user prompt loop and the connection manager concurrently
    await asyncio.gather(
        session_input_loop(session_queue),
        connection_manager(initial_session, session_queue),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nListener stopped by user.")