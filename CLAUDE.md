# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Tiger's Day** is a digital implementation of a historical strategy board game simulating the Anglo-Mysore Wars (1767–1799). Two players (British East India Company vs. Kingdom of Mysore) compete for territorial control across 23 territories in India. Includes an AlphaZero-style self-play AI training system.

## Environment Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
# Dependencies: numpy, torch
```

## Running

```bash
# Game logic smoke tests (via __main__ blocks)
python game/engine.py   # MoveEngine with default game state, prints legal moves
python game/state.py    # GameState initialization

# Train the AI
python train.py --iterations 100 --games 50 --simulations 100
python train.py --resume ai/checkpoints/best_model.pth  # resume training
```

There is no formal test framework. Components are tested via `if __name__ == "__main__"` blocks.

## Architecture

### Core Game Logic (`game/`)

- **`state.py` — `GameState`**: Encodes the entire game state as a 138-element boolean NumPy vector:
  - `[0:6]` British cards in hand (6 cards)
  - `[6:12]` Mysore cards in hand (6 cards)
  - `[12:81]` Territory states — 23 territories × 3 states (fresh army / tired army / fort)
  - `[81:85]` Turn order (one-hot, 4 turns per round)
  - `[85:88]` Who moves next: British Move, Mysore Card, or British Card (one-hot)
  - `[88:92]` Combat strength for Mysore (one-hot, 4 levels)
  - `[92:138]` Combatants — 23×2 boolean (attacker / defender territory)

- **`engine.py` — `MoveEngine`**: Generates a **636-element move validity mask** encoding all legal moves. Three phases:
  - Phase 1 (British Move, 101 actions): 78 edge moves + 23 tire actions
  - Phase 2 (Mysore Card, 101 actions): card plays, draws, power, pass
  - Phase 3 (British Card, 434 actions): card plays, draws, power, pass (includes 207 Royal Navy matrix)
  - Uses adjacency matrix (23×23), edge arrays (78 edges), coastal positions (9 territories), key territories (5 cities)

- **`updater.py` — `GameUpdater`**: Takes a move index (0–635) + GameState → new GameState. Handles all 22 move types, combat resolution, turn advancement, and luck turn signaling. Returns `(new_state, game_result, luck_turn_info)`.

- **`winchecker.py` — `WinChecker`**: Checks win conditions — British win (army in all 5 keys), Mysore win (no British armies OR survived Turn 4).

### AI System (`ai/`)

- **`model.py` — `TigerNet`**: PyTorch MLP (512→256→256 shared trunk, policy head → 636D logits, value head → scalar in [-1,1]). `predict()` for single-state MCTS inference, `forward()` for batch training.

- **`mcts.py` — `MCTS`**: AlphaZero-style tree search with PUCT selection, Dirichlet noise at root, subtree reuse. Handles "luck turns" (random card discards) via `resolve_luck()` — these are not saved for training.

- **`trainer.py` — `Trainer`**: Self-play loop + training. Plays games via MCTS, collects `(state, mcts_policy, outcome)` examples into a replay buffer, trains with AlphaZero loss: `L = (z-v)² - π·log(p) + c||θ||²`.

### Frontend (`frontend/`)

- **`index.html`**: Single-page app using **PyScript** to run Python game logic in the browser. Contains the full SVG game board with WebSocket client for server communication.

### Server (`server/`)

Stubs for a WebSocket-based multiplayer backend (`app.py`, `sockets.py`).

## Key Design Decisions

- **British combat strength** is NOT stored in the 138D state vector. It's passed locally within the updater during the same impulse (from British Power move to combat resolution).
- **Luck turns** (random card discards from combat loss or Cavalry Raid) are handled outside the state vector via a return flag. MCTS resolves them with RNG and does NOT save them as training examples.
- **Combat adjacency**: each side counts their OWN pieces adjacent to the defending fort. The attacking army at its source is automatically counted in British's adjacency.
- **Turn ends** when no fresh armies remain at the start of an impulse (British Move phase).

## Key Constants

| Constant | Value | Purpose |
|---|---|---|
| `NODES` | 23 | Total map territories |
| `EDGES` | 78 | Directed movement edges |
| `COASTAL_INDICES` | 9 entries | Coastal territories for Royal Navy |
| `KEY_INDICES` | 5 entries | Victory-relevant cities (indices 0–4) |
| Move vector size | 636 | Total possible actions per state |
| State vector size | 138 | Full game state encoding |
