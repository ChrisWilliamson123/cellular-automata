import json

from enum import StrEnum
from fastapi import WebSocket
from typing import Any

from webapp.web_automata_runner import WebAutomataRunner

class MessageReceiver():
    class MessageType(StrEnum):
        TOGGLE_PAUSE = 'togglePause'
        RESET = 'reset'
        CHANGE_FRAMERATE_MULTIPLIER = 'changeFramerateMultiplier'
        CHANGE_AUTOMATON = 'changeAutomaton'
        TOGGLE_REWIND = 'toggleRewind'

    def __init__(self, ws: WebSocket, runner: WebAutomataRunner):
        self.ws = ws
        self.runner = runner

    async def receive_messages(self):
        while True:
            received_text = await self.ws.receive_text()
            json_data = json.loads(received_text)

            type: str = json_data['type']
            data: Any = json_data.get('data', None)

            if type == MessageReceiver.MessageType.TOGGLE_PAUSE:
                self.runner.toggle_paused()
            elif type == MessageReceiver.MessageType.RESET:
                await self.runner.reset_automaton()
            elif type == MessageReceiver.MessageType.CHANGE_FRAMERATE_MULTIPLIER:
                self.runner.change_framerate_multiplier(float(data))
            elif type == MessageReceiver.MessageType.CHANGE_AUTOMATON:
                self.runner.change_automaton(data)
            elif type == MessageReceiver.MessageType.TOGGLE_REWIND:
                self.runner.toggle_rewind()