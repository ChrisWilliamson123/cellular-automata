import asyncio
import json

from fastapi import WebSocket
from typing import List

from automata.automaton import AutomatonRewindError
from automata.binary.binary_automaton import RandomBinaryAutomaton
from automata.binary.builder import binary_automata_from_config, random_binary_automaton_from_config
from webapp.message_sender import MessageSender
from webapp.state import RunnerState

class WebAutomataRunner():
    AUTOMATON_SIZE = (300, 300)
    INITIAL_FRAMERATE = 30

    @property
    def framerate(self):
        return self.state.framerate_multiplier * WebAutomataRunner.INITIAL_FRAMERATE

    def __init__(self, ws: WebSocket):
        self.state = RunnerState(on_change_fn=lambda state: asyncio.ensure_future(self.message_sender.send_message('state', state)))
        self.message_sender = MessageSender(ws)
        self._load_automata()

    async def start(self):
        await self._send_init_message()
        await self._run()

    async def _run(self):
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

            await asyncio.gather(self._render_automaton(), self._send_metadata_message())

            elapsed = asyncio.get_event_loop().time() - start
            delay = max(0, (1 / self.framerate) - elapsed)
            await asyncio.sleep(delay)   

    def _load_automata(self):
        with open('configs/binary-automata.json') as f:
            self.configs: List[dict] = json.load(f)

        self.automata_names: List[str] = [a['name'] for a in self.configs]
        self._select_automaton(self.automata_names[0])

    def _select_automaton(self, automaton_name):
        config = list(filter(lambda c: c['name'] == automaton_name, self.configs))[0]
        if config['type'] == 'binary':
            self.automaton = binary_automata_from_config(config, WebAutomataRunner.AUTOMATON_SIZE)()
        elif config['type'] == 'binary-random':
            self.automaton = random_binary_automaton_from_config(config, WebAutomataRunner.AUTOMATON_SIZE)()

    async def _send_init_message(self):
        """Sends the automata names and initial render of the selected automaton"""
        data = {
            "automataNames": self.automata_names
        }

        await asyncio.gather(self.message_sender.send_message('init', data), self._render_automaton())

    async def _send_metadata_message(self):
        """Sends metadata for the currently running automaton"""
        metadata = {
            "subtitle": self.automaton.subtitle(),
            "totalIterations": self.automaton.total_iterations,
            "iterationIndex": self.automaton.iteration_index,
            "isRandomBinaryAutomaton": isinstance(self.automaton, RandomBinaryAutomaton)
        }

        await self.message_sender.send_message('automatonMetadata', metadata)

    async def _render_automaton(self):
        frame = self.automaton.get_frame()
        await self.message_sender.send_bytes(frame.tobytes())

    # RECEIVING MESSAGES
    def toggle_paused(self):
        self.state.toggle_paused()

    async def reset_automaton(self):
        self.automaton.reset()
        await self._render_automaton()

    def change_framerate_multiplier(self, multiplier):
        self.state.framerate_multiplier = multiplier

    def change_automaton(self, new_automaton_name):
        self._select_automaton(new_automaton_name)

    def toggle_rewind(self):
        self.state.toggle_rewind()

    def randomise_notation(self):
        if isinstance(self.automaton, RandomBinaryAutomaton):
            self.automaton.randomise_notation()