import asyncio
import json
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config

with open('configs/automata.json') as f:
    configs = json.load(f)

builder_map = {
    'binary': binary_automata_from_config,
    'forest-fire': forest_fire_automata_from_config,
    'brians-brain': brians_brain_automata_from_config
}

automaton_size = (300, 300)

gol_config = list(filter(lambda c: c['name'] == 'Game of Life', configs))[0]
gol = binary_automata_from_config(gol_config, automaton_size)
aut = gol()

app = FastAPI()

async def automaton(ws: WebSocket):
    framerate = 60 # Frames per second
    running = True
    sent_metadata = False
    rule = "Game of Life"

    await ws.accept()
    while True:
        try:
            msg = await asyncio.wait_for(ws.receive_text(),timeout=1 / framerate)
            msg = json.loads(msg)
            if msg["type"] == "toggle":
                running = not running
            elif msg["type"] == "rule":
                rule = msg["rule"]
            elif msg["type"] == "reset":
                aut.reset()
            elif msg["type"] == "framerate":
                framerate = int(msg["framerate"])
        except asyncio.TimeoutError:
            pass

        if not sent_metadata:
            await ws.send_text(json.dumps({
                "type": "subtitle",
                "data": aut.subtitle()
            }))
            sent_metadata = True

        if running:
            aut.iterate(0)
            frame = aut.get_frame()
            await ws.send_bytes(frame.tobytes())

        await asyncio.sleep(1 / framerate)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await automaton(ws)

app.mount("/", StaticFiles(directory="static", html=True), name="static")