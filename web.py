import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from webapp.message_receiver import MessageReceiver
from webapp.web_automata_runner import WebAutomataRunner

app = FastAPI()

@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    runner = WebAutomataRunner(ws)
    message_receiver = MessageReceiver(ws, runner)

    await asyncio.gather(runner.start(), message_receiver.receive_messages())

app.mount('/', StaticFiles(directory='webapp/static', html=True), name='static')