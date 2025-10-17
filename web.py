import asyncio
from dataclasses import dataclass
import json
from typing import Any, List, Self, TypeVar
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from automata.automaton import AutomatonRewindError
from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config
from webapp.state import RunnerState

# builder_map = {
#         'binary': binary_automata_from_config,
#         'forest-fire': forest_fire_automata_from_config,
#         'brians-brain': brians_brain_automata_from_config
#     }

# class WebHaj(AutomatonDelegate):

class WebHandler():
    AUTOMATON_SIZE = (300, 300)
    INITIAL_FRAMERATE = 30

    def __init__(self, ws: WebSocket):
        self.ws = ws

        with open('configs/binary-automata.json') as f:
            self.configs: List[dict] = json.load(f)

        self.automata_names: List[str] = [a['name'] for a in self.configs]
        self.automaton = binary_automata_from_config(self.configs[0], WebHandler.AUTOMATON_SIZE)()

        self.state = RunnerState(on_change_fn=lambda state: asyncio.ensure_future(self._send_state_message(state)))

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
        await self.ws.send_json(state)

    async def _handle_messages(self):
        while True:
            msg = await self.ws.receive_text()
            msg = json.loads(msg)

            type: str = msg['type']
            data: Any = msg.get('data', None)

            if type == 'togglePause':
                self.state.is_paused = not self.state.is_paused
            elif type == 'reset':
                self.automaton.reset()
                await self._render_automaton()
            # elif msgType == 'framerate':
            #     self.state.framerate = int(msg['framerate'])
            elif type == "framerateMultiplier":
                self.state.framerate_multiplier = float(data)
            elif type == 'changeAutomata':
                config = list(filter(lambda c: c['name'] == data, self.configs))[0]
                self.automaton = binary_automata_from_config(config, (300, 300))()
            elif type == 'rewind':
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

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    handler = WebHandler(ws)
    await handler.begin()

app.mount("/", StaticFiles(directory="static", html=True), name="static")