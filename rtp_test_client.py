import asyncio
import websockets

async def test_receiver():
    uri = "ws://127.0.0.1:8000/ws/voice-bot/?agent_id="

    print("Connecting to WebSocket...")

    async with websockets.connect(uri) as ws:
        print("Connected!")

        with open("received_ulaw.raw", "wb") as f:
            while True:
                data = await ws.recv()

                if isinstance(data, bytes):
                    # Remove RTP header (12 bytes)
                    payload = data[12:]
                    f.write(payload)
                    print("Received audio chunk:", len(payload))
                else:
                    print("Text message:", data)

asyncio.run(test_receiver())