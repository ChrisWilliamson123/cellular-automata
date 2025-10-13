# Cellular Automata
A collection of cellular automata that are visualised through the Pygame framework.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
source .venv/bin/activate
python main.py
```

## Controls
| Key   | Action                   |
|:------|:-------------------------|
| SPACE | Pause current automaton  |
| R     | Reset current automaton  |
| LEFT  | Go to previous automaton |
| RIGHT | Go to next automaton     |
| UP    | Increase speed           |
| DOWN  | Decrease speed           |

## Configuration
The individual automata settings can be configured in `main.py`. The binary automata have their birth/survival rules configured using [B/S notation](https://en.wikipedia.org/wiki/Life-like_cellular_automaton). For example, Game of Life has notation B3/S23.
