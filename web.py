import asyncio
from dataclasses import dataclass
import json
from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from automata.automaton import AutomatonRewindError
from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config

# builder_map = {
#         'binary': binary_automata_from_config,
#         'forest-fire': forest_fire_automata_from_config,
#         'brians-brain': brians_brain_automata_from_config
#     }

# class WebHandlerAutomatonDelegate(AutomatonDelegate):

class State:
    def __init__(self, on_change_fn):
        self._is_paused = False
        self._is_rewinding = False
        self._framerate_multiplier: float = 1
        self.on_change_fn = on_change_fn

    @property
    def json(self):
        return {
            "type": "state",
            "data": {
                "isPaused": self.is_paused,
                "isRewinding": self.is_rewinding,
                "framerateMultiplier": self.framerate_multiplier
            }
        }

    # is_paused
    @property
    def is_paused(self):
        return self._is_paused

    @is_paused.setter
    def is_paused(self, value: bool):
        self._is_paused = value
        self.on_change_fn(self.json)

    def toggle_paused(self):
        self.is_paused = not self._is_paused
    
    # is_rewinding
    @property
    def is_rewinding(self):
        return self._is_rewinding

    @is_rewinding.setter
    def is_rewinding(self, value: bool):
        self._is_rewinding = value
        self.on_change_fn(self.json)
    
    def toggle_rewind(self):
        self.is_rewinding = not self.is_rewinding

    # framerate
    @property
    def framerate_multiplier(self):
        return self._framerate_multiplier

    @framerate_multiplier.setter
    def framerate_multiplier(self, value: float):
        self._framerate_multiplier = value
        self.on_change_fn(self.json)

class WebHandler():
    AUTOMATON_SIZE = (300, 300)
    INITIAL_FRAMERATE = 30

    def __init__(self, ws: WebSocket):
        self.ws = ws

        with open('configs/binary-automata.json') as f:
            self.configs = json.load(f)

        self.automata_names = [a['name'] for a in self.configs]
        self.automaton = binary_automata_from_config(self.configs[0], WebHandler.AUTOMATON_SIZE)()

        self.state = State(on_change_fn=lambda state: asyncio.ensure_future(self._send_state_message(state)))

        self.msg_task = asyncio.create_task(self._handle_messages())
        self.run_task = asyncio.create_task(self._run_automaton())

    @property
    def framerate(self):
        return self.state.framerate_multiplier * WebHandler.INITIAL_FRAMERATE

    async def begin(self):
        await self._send_init_message()
        await self._send_state_message(self.state.json)
        await asyncio.gather(self.msg_task, self.run_task)

    async def _send_init_message(self):
        init_message = {
            "type": "init",
            "data": {
                "automataNames": self.automata_names
            }
        }
        await self.ws.send_json(init_message)

    async def _send_state_message(self, state):
        print(f'Sending state: {state}')
        await self.ws.send_json(state)

    async def _handle_messages(self):
        while True:
            msg = await self.ws.receive_text()
            msg = json.loads(msg)
            msgType = msg['type']
            if msgType == 'togglePause':
                self.state.is_paused = not self.state.is_paused
            elif msgType == 'reset':
                self.automaton.reset()
                await self._render_automaton()
            # elif msgType == 'framerate':
            #     self.state.framerate = int(msg['framerate'])
            elif msgType == "framerateMultiplier":
                self.state.framerate_multiplier = float(float(msg['multiplier']))
            elif msgType == 'changeAutomata':
                config = list(filter(lambda c: c['name'] == msg['name'], self.configs))[0]
                self.automaton = binary_automata_from_config(config, (300, 300))()
            elif msgType == 'rewind':
                self.state.is_rewinding = not self.state.is_rewinding

    def _build_metadata_message(self):
        metadata = {
            "subtitle": self.automaton.subtitle(),
            "totalIterations": self.automaton.total_iterations,
            "iterationIndex": self.automaton.iteration_index
        }

        full_message = {
            "type": "metadata",
            "data": metadata
        }

        return full_message

    async def _run_automaton(self):
        while True:
            start = asyncio.get_event_loop().time()

            if not self.state.is_paused:
                if self.state.is_rewinding:
                    try:
                        self.automaton.rewind()
                    except AutomatonRewindError:
                        self.state.toggle_rewind()
                        self.state.toggle_paused()
                else:
                    self.automaton.iterate(0)


            await self._render_automaton()

            elapsed = asyncio.get_event_loop().time() - start
            delay = max(0, (1 / self.framerate) - elapsed)
            await asyncio.sleep(delay)

    async def _render_automaton(self):
        frame = self.automaton.get_frame()

        await self.ws.send_bytes(frame.tobytes())
        await self.ws.send_json(self._build_metadata_message())

    def did_change_rewind(self, isRewinding):
        asyncio.ensure_future(
            self.ws.send_json({
                "type": "rewind",
                "data": {
                    "isRewinding": isRewinding
                }
            })
        )

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    handler = WebHandler(ws)
    await handler.begin()

app.mount("/", StaticFiles(directory="static", html=True), name="static")