from typing import Callable

class RunnerState:
    def __init__(self, on_change_fn: Callable[[dict], None]):
        self._is_paused = False
        self._is_rewinding = False
        self._framerate_multiplier: float = 1
        self.on_change_fn = on_change_fn

    @property
    def json(self):
        return {
            "isPaused": self.is_paused,
            "isRewinding": self.is_rewinding,
            "framerateMultiplier": self.framerate_multiplier
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