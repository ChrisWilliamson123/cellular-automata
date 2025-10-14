# server.py
import asyncio
import json
import time
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config

FRAMERATE = 60 # Frames per second

ALIVE_COLOUR = (255, 255, 255)

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

# while True:
#     automaton.iterate(0)
#     if automaton.iterations > 0 and automaton.iterations % 1000 == 0:
#         current = time.time()
#         print(automaton.iterations, f'{1 / ((current - start) / automaton.iterations):.0f} FPS')

app = FastAPI()

async def automaton(ws: WebSocket):
    running = True
    rule = "Game of Life"

    await ws.accept()
    while True:
        try:
            msg = await asyncio.wait_for(ws.receive_text(),timeout=1 / FRAMERATE)
            msg = json.loads(msg)
            if msg["type"] == "toggle":
                running = not running
            elif msg["type"] == "rule":
                rule = msg["rule"]
        except asyncio.TimeoutError:
            pass

        if running:
            aut.iterate(0)

            frame = aut.get_frame()

            await ws.send_bytes(frame.tobytes())

        await asyncio.sleep(1 / FRAMERATE)

def step(grid, rule):
    # Example simple rule (replace with yours)
    n = sum(np.roll(np.roll(grid, i, 0), j, 1)
            for i in (-1, 0, 1) for j in (-1, 0, 1)
            if not (i == j == 0))
    return ((n == 3) | (grid & (n == 2))).astype(np.uint8)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await automaton(ws)
    # await ws.accept()
    # while True:
    #     data = await ws.receive_text()
    #     await ws.send_text(f"Message text was: {data}")

app.mount("/", StaticFiles(directory="static", html=True), name="static")