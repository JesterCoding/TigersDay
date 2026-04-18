# Tiger’s Day AI Implementation

Welcome to the AI and engine implementation for **Tiger’s Day**, a strategic board game simulating the Anglo-Mysore Wars between Tipu Sultan (Sultanate of Mysore) and Cornwallis (East India Company). 

This repository contains the pure game logic, a Deep Learning/Monte Carlo Tree Search (MCTS) AI built to master the game, and a FastAPI/WebSocket backend to visualize gameplay and evaluate positions.

---

## 📖 The Game: Tiger's Day

### Overview
* **Asymmetric Gameplay:** Sultanate of Mysore (Forts) vs. East India Company (Armies).
* **Duration:** 4 turns representing the 4 Anglo-Mysore Wars.
* **Objective:** The British win by occupying all 5 key territories with an army. Mysore wins by surviving until the end of Turn 4 or eliminating all British armies.

### Core Rules
* Neither armies nor forts can share a space, and forts cannot move.
* Both sides draw 6 cards per turn, and British armies become Fresh.
* Players alternate playing impulses until all British armies are Tired.
* Combat is triggered when an army moves into an adjacent fort, with higher strength winning and ties going to Mysore.
* Cards can be played for text effects, to draw lower-numbered cards, or to add their power to unresolved battles.

---

## 🧠 AI Architecture

The AI relies on a combination of Deep Multi-Layer Perceptrons (MLP) and Monte Carlo Tree Search (MCTS), inspired by AlphaZero.

### Game State Representation
The game state is encoded into a 143D Vector representing the board:
* 6 indices for British Cards.
* 6 indices for Mysore Cards.
* 23 3D vectors holding territory info (fresh army, tired army, fort), where empty is `[0,0,0]`.
* The turn order indicating Turns 1 through 4.
* Turn indicator for who is to move (British to move, Mysore Card, British Card), where luck bypasses are encoded as `[0,0,0]`.
* Mysore existing card Combat Strength (0/1/2/3) to eliminate battle ambiguity.
* Attacker and defender locations mapped as `[23, 23]`.

This creates a state space of $\sim7.3 \times 10^{21}$ possible game states and a theoretical move space of $\sim10^{60}$.

### Neural Net Player + Evaluator
A deep neural network acts as a black box evaluator. 
* **Policy ($p$):** Takes the Game State and outputs the probabilities of the network's choice for a move across the maximum theoretical move space, unnormalized.
* **Value ($v$):** Outputs a scalar evaluation (-1, 0, 1) estimating who is currently winning or tied.

### Tree Search (MCTS)
* Executes a fixed number of simulations to think before committing to a move.
* Taps the Neural Net to mask and normalize valid moves from the unnormalized policy output.
* Balances Exploitation and Exploration to dive deeper into promising lines.
* Once a move is picked, it saves a snapshot, updates the root to the chosen subtree, and discards the rest.
* "Luck" elements bypass the Neural Net evaluation and use RNG to expand random outcomes.
* "Luck" turns are explicitly not saved for backpropagation training.

### AI Updater (Training)
Runs backpropagation on the Player/Evaluator using MCTS simulation results. 

**Cost Function:**
$$L = (z - v)^2 - \pi \cdot \log(p) + c||\theta||^2$$

* **Value Loss** $(z - v)^2$: Mean Squared Error between the actual game winner ($z$) and the Evaluator's prediction ($v$).
* **Policy Loss** $-\pi \cdot \log(p)$: Cross-Entropy between MCTS deep visit counts ($\pi$) and the raw Policy prediction ($p$).
* **Regularization** $c||\theta||^2$: A penalty on the weights to prevent the AI from overfitting.

---

## ⚙️ Game Engine Components

* **Move Engine:** Takes the Game State Representation and outputs a mask of the theoretical maximum move space. This space contains all theoretically possible moves independent of the current state.
* **Game Updater:** Takes the chosen move and current state to output the newly updated Game State. It resolves battles and handles random card discarding.
* **WinChecker:** Runs at the end of every impulse. It evaluates if armies occupy all keys, if Turn 4 ended, or if all British armies are eliminated.
* **Move Representation:** Utilizes a unique prime factorization trick to log and store games. This enables an interactive sequence log allowing players to go back-and-forth through previous board states.

---

## 🖥️ Game UI
The user interface serves as the visual bridge for the engine.
* Visualizes the current game state representation.
* Displays an active "Stockfish-style" evaluation bar querying the AI Evaluator.
* Shows the top 3 moves the AI is actively considering alongside their respective evaluations.
* Logs the full sequence of moves for visual playback.

---

## 📁 Project Structure

```text
TIGERSDAY/
├── ai/                      # Machine Learning / AI Opponent
│   ├── checkpoints/         # Saved model weights
│   ├── models/              # Active Neural Network architectures
│   ├── mcts.py              # Monte Carlo Tree Search logic
│   ├── multitrain.py        # Multi-threaded training logic
│   ├── neural.py            # Neural Network definitions
│   ├── train.py             # Standard AI training loop
│   └── visualizer.py        # Terminal evaluation viewer
│
├── api/                     # Backend API layer
├── checkpoints/             # Global system checkpoints
│
├── game/                    # Pure game logic
│   ├── __init__.py
│   ├── constants.py         # Game constants and dimensions
│   ├── engine.py            # Move masking and generation
│   ├── state.py             # Vector state representation
│   └── updater.py           # State transition and combat logic
│
├── public/                  # Frontend UI and static assets
│
├── .gitignore
├── .vercelignore
├── README.md                # Documentation
├── requirements-dev.txt
├── requirements.txt         # Dependencies
├── server.py                # Server entry point
└── vercel.json              # Deployment configuration