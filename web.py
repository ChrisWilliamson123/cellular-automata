import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from automata.automaton import Automaton, AutomatonDelegate
from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config

# builder_map = {
#         'binary': binary_automata_from_config,
#         'forest-fire': forest_fire_automata_from_config,
#         'brians-brain': brians_brain_automata_from_config
#     }

# class WebHandlerAutomatonDelegate(AutomatonDelegate):

class WebHandler(AutomatonDelegate):
    AUTOMATON_SIZE = (300, 300)
    INITIAL_FRAMERATE = 30

    def __init__(self, ws: WebSocket):
        self.ws = ws

        with open('configs/binary-automata.json') as f:
            self.configs = json.load(f)

        self.automata_names = [a['name'] for a in self.configs]
        self.automaton = binary_automata_from_config(self.configs[0], WebHandler.AUTOMATON_SIZE)()
        self.automaton.delegate = self

        self.state = {
            "running": True,
            "framerate": WebHandler.INITIAL_FRAMERATE,
            "automata_names": self.automata_names,
            "configs": self.configs
        }

        self.msg_task = asyncio.create_task(self._handle_messages())
        self.run_task = asyncio.create_task(self._run_automaton())

    async def begin(self):
        await self._send_init_message()
        await asyncio.gather(self.msg_task, self.run_task)

    async def _send_init_message(self):
        init_message = {
            "type": "init",
            "data": {
                "framerate": self.state["framerate"],
                "automataNames": self.state['automata_names']
            }
        }
        await self.ws.send_json(init_message)

    async def _handle_messages(self):
        while True:
            msg = await self.ws.receive_text()
            msg = json.loads(msg)
            msgType = msg['type']
            if msgType == 'toggle':
                self.automaton.toggle_pause()
            elif msgType == 'reset':
                self.automaton.reset()
            elif msgType == 'framerate':
                self.state['framerate'] = int(msg['framerate'])
            elif msgType == "framerateMultiplier":
                self.state['framerate'] = int(WebHandler.INITIAL_FRAMERATE * float(msg['multiplier']))
            elif msgType == 'changeAutomata':
                config = list(filter(lambda c: c['name'] == msg['name'], self.configs))[0]
                self.automaton = binary_automata_from_config(config, (300, 300))()
            elif msgType == 'rewind':
                self.automaton.reverse = not self.automaton.reverse

    def _build_metadata_message(self):
        metadata = {
            "subtitle": self.automaton.subtitle(),
            "iterations": self.automaton.iteration_count,
            "isPaused": self.automaton.paused,
            "isRewinding": self.automaton.reverse
        }

        full_message = {
            "type": "metadata",
            "data": metadata
        }

        return json.dumps(full_message)

    async def _run_automaton(self):
        while True:
            start = asyncio.get_event_loop().time()

            if self.state["running"]:
                self.automaton.iterate(0)

                frame = self.automaton.get_frame()

                await self.ws.send_bytes(frame.tobytes())
                await self.ws.send_text(self._build_metadata_message())

            elapsed = asyncio.get_event_loop().time() - start
            delay = max(0, (1 / self.state["framerate"]) - elapsed)
            await asyncio.sleep(delay)

    def did_change_rewind(self, isRewinding):
        asyncio.ensure_future(
            self.ws.send_json({
                "type": "rewind",
                "data": {
                    "isRewinding": isRewinding
                }
            })
        )

    async def ws_send_json(self, json):
        await self.ws.send_json(json)

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    handler = WebHandler(ws)
    await handler.begin()

app.mount("/", StaticFiles(directory="static", html=True), name="static")