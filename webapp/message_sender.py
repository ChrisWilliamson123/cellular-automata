from typing import Any
from fastapi import WebSocket

class MessageSender():
    def __init__(self, ws: WebSocket):
        self.ws = ws

    async def send_message(self, type: str, data: Any):
        await self.ws.send_json({ 'type': type, 'data': data })

    async def send_bytes(self, data: bytes):
        await self.ws.send_bytes(data)