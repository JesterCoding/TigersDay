# Tiger’s Day AI Implementation

Welcome to the AI and engine implementation for **Tiger’s Day**, a strategic board game simulating the Anglo-Mysore Wars between Tipu Sultan (Sultanate of Mysore) and Cornwallis (East India Company). 

This repository contains the pure game logic, a Deep Learning/Monte Carlo Tree Search (MCTS) AI built to master the game, and a FastAPI/WebSocket backend to visualize gameplay and evaluate positions.

---

## 📖 The Game: Tiger's Day

### Overview
* **Asymmetric Gameplay:** Sultanate of Mysore (Forts) vs. East India Company (Armies).
* **Duration:** 4 turns (each turn represents 1 of the 4 Anglo-Mysore Wars).
* **Objective:** * **British Win:** Occupy all 5 key territories with an army.
    * **Mysore Win:** Survive until the end of Turn 4, or eliminate all British armies.

### Core Rules
* **Setup:** Neither armies nor forts can share a space. Forts cannot move; armies move once per war (unless modified by cards).
* **Turn Sequence:** Both sides draw 6 cards. British armies become *Fresh*. Players alternate playing impulses until all British armies are *Tired*.
* **Impulses:** * British move a *Fresh* army (making it *Tired*).
    * Mysore may play a card.
    * British may play a card.
    * Resolve battles.
* **Combat:** Triggered when an army moves into an adjacent fort. Base strength is 1 per adjacent friendly fort/army + card modifiers. Ties go to Mysore. Losing armies become *Tired* in place; losing forts are removed. Losers must discard a card randomly.

### The Cards
Cards can be played for their text, to draw a lower-numbered card, or to add their number to combat strength. 
* **Mysore (Forts):** Iron Rockets (3), Sepoy Mutiny (2), French Alliance (2), Cavalry Raid (1), Sea Trade (1), Monsoon (1).
* **British (Armies):** Wall Breach (3), Highlanders (2), Royal Navy (2), Divide and Rule (1), Force March (1), Princely States (1).

*(Potential upcoming rule changes: Ceylon to Trichy, Sea Trade modifications, Tire in place).*

---

## 🧠 AI Architecture

The AI relies on a combination of Deep Multi-Layer Perceptrons (MLP) and Monte Carlo Tree Search (MCTS), heavily inspired by AlphaZero.

### Game State Representation
The game state is encoded into a **138D Vector** to feed into the neural network:
* 6 for British Cards
* 6 for Mysore Cards
* 23 3D vectors holding territory info (fresh army, tired army, fort). Empty is `[0,0,0]`.
* Turn order (Turns 1-4).
* Impulse state (British to move, Mysore Card, British Card). "Luck" transitions bypass this via `[0,0,0]`.
* Active combat strengths (0/1/2/3) to remove battle ambiguity.
* Attacker and defender locations `[23, 23]`.

**State Space:** $\sim7.3 \times 10^{21}$ possible game states, with a theoretical move space of $\sim10^{60}$. 

### Neural Network Player + Evaluator
A Deep MLP with 3 to 4 hidden layers (512 -> 256 -> 256 neurons). It acts as a black box that takes in the 138D Game State and outputs:
1.  **Policy ($p$):** Probabilities for the neural network’s choice of move across the theoretical move space.
2.  **Value ($v$):** A scalar evaluation (`-1`, `0`, `1`) estimating who is winning.

### Tree Search (MCTS)
* Executes a fixed number of simulations to look ahead before committing to a move.
* Uses the Neural Net's policy output ($P_t$) to mask and normalize valid moves.
* Balances Exploitation and Exploration (UCB) to dive deeper into promising lines.
* Once a move is selected, the chosen subtree becomes the new root; the rest is discarded.
* "Luck" elements (random card discards) bypass the neural net evaluation and use RNG to expand random outcomes.

### AI Updater (Training)
Runs backpropagation on the Player/Evaluator using MCTS simulation results. 

**Cost Function:**
$$L = (z - v)^2 - \pi \cdot \log(p) + c||\theta||^2$$

* **Value Loss** $(z - v)^2$: Mean Squared Error between the actual game winner ($z$) and the Evaluator's prediction ($v$).
* **Policy Loss** $-\pi \cdot \log(p)$: Cross-Entropy between MCTS deep visit counts ($\pi$) and the raw Policy prediction ($p$).
* **Regularization** $c||\theta||^2$: Prevents the AI from overfitting.

---

## ⚙️ Game Engine Components

* **Move Engine:** Takes the Game State Representation and outputs a mask on $V_t$ (the constant 590-dimensional theoretical move space).
    * *Breakdown of $V_t$ (590 Moves):* British Move (101) + Mysore Card (101) + British Card (434) = 636 total defined actions max, masked to 590 per impulse.
* **Game Updater:** Takes the MCTS chosen move and current state, outputs the new state. It resolves battles, handles RNG for card discarding, and triggers the win checker.
* **WinChecker:** Evaluates the state at the end of every impulse to check if British armies occupy all keys, if Turn 4 has ended, or if British armies are eradicated.

---

## 📈 Training & Curriculum Learning

To speed up convergence, the AI is trained using Curriculum Learning—moving from simplified end-games to the full complex start position as the loss decreases.

* **Stage 0:** 5 armies in keys, 1 random fort + 2 random impulses (Turn 4).
* **Stage 1:** 4 armies in key, 1 fort in key, 1 army random spot + 2 random impulses (Turn 4).
* **Stage 2:** 5 armies on coast, 1 key fort + 2 random impulses (Turn 4).
* **Stage 3:** Setup armies/forts in 1 key + play full Turn 3 randomly.
* **Stage 4:** Setup armies/forts in both keys + play 2 random impulses of Turn 3.
* **Stage 5:** Full position minus 3 forts + play Turn 2 randomly.
* **Stage 6:** Full position minus 2 forts (Turn 1).
* **Stage n:** Standard Game Setup (Turn 1).

**Sample Training Command:**
```bash
python3 train.py --iterations 200 --simulations 500 --lr 0.5 --resume


tigers_day_ai/
│
├── server.py              # Entry point to run the FastAPI web server for the UI
├── train.py               # Entry point to run the self-play and AI training loop
├── requirements.txt       # PyTorch, FastAPI, Uvicorn, Numpy, etc.
├── .gitignore
│
├── game/                  # Pure game logic (No AI, No UI)
│   ├── __init__.py
│   ├── state.py           # GameState class (handles the 138D vector encoding)
│   ├── engine.py          # MoveEngine (generates the 590D mask of legal moves)
│   ├── updater.py         # GameUpdater (applies moves, resolves battles/discards)
│   └── constants.py       # Constants (23 Nodes, 5 Keys, 39 Edges, 9 Coasts)
│
├── ai/                    # Neural Network & Tree Search
│   ├── __init__.py
│   ├── model.py           # PyTorch Deep MLP (Shared layers + Policy/Value heads)
│   ├── mcts.py            # Monte Carlo Tree Search (Simulations, UCB)
│   ├── trainer.py         # Self-play, memory buffers, backpropagation
│   └── checkpoints/       # Trained .pth model weights
│
├── server/                # Backend API layer
│   ├── __init__.py
│   ├── app.py             # FastAPI application setup
│   └── sockets.py         # WebSocket handlers (streams eval/moves to UI)
│
└── frontend/              # Static UI files served by FastAPI
    ├── index.html         # Main game layout
    ├── css/
    │   └── style.css      # Grid layouts, card styling
    └── js/
        ├── ui.js          # Handles visual updates (moving pieces, eval bar)
        └── socket.js      # Listens to Python backend via WebSockets