import asyncio
import json
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from automata.automaton import Automaton
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

app = FastAPI()

def build_metadata_message(automaton: Automaton):
    metadata = {
        "subtitle": automaton.subtitle(),
        "iterations": automaton.iterations
    }

    full_message = {
        "type": "metadata",
        "data": metadata
    }

    return json.dumps(full_message)

async def handle_messages(ws, aut, state):
    while True:
        msg = await ws.receive_text()
        msg = json.loads(msg)
        if msg["type"] == "toggle":
            state["running"] = not state["running"]
        elif msg["type"] == "rule":
            state["rule"] = msg["rule"]
        elif msg["type"] == "reset":
            aut.reset()
        elif msg["type"] == "framerate":
            state["framerate"] = int(msg["framerate"])

async def run_automaton(ws, aut, state):
    while True:
        start = asyncio.get_event_loop().time()

        if state["running"]:
            aut.iterate(0)
            frame = aut.get_frame()
            await ws.send_bytes(frame.tobytes())
            
            await ws.send_text(build_metadata_message(aut))

        elapsed = asyncio.get_event_loop().time() - start
        delay = max(0, (1 / state["framerate"]) - elapsed)
        await asyncio.sleep(delay)

INITIAL_FRAMERATE = 1

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    state = { "running": True, "rule": "Game of Life", "framerate": INITIAL_FRAMERATE }

    gol_config = list(filter(lambda c: c['name'] == 'Game of Life', configs))[0]
    aut = binary_automata_from_config(gol_config, (300, 300))()

    init_message = {
        "type": "init",
        "data": {
            "framerate": state["framerate"]
        }
    }
    await ws.send_json(init_message)

    msg_task = asyncio.create_task(handle_messages(ws, aut, state))
    run_task = asyncio.create_task(run_automaton(ws, aut, state))

    await asyncio.gather(msg_task, run_task)


app.mount("/", StaticFiles(directory="static", html=True), name="static")