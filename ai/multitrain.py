import os
import random
import argparse
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

import torch.multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

import game.updater as Updater
import game.engine as Engine
from game.constants import *
from ai.mcts import MCTS
from ai.neural import AlphaTiger, load_checkpoint, save_checkpoint
from game.state import GameState
from ai.train import *


# ─── Data structures ──────────────────────────────────────────────────────────

Sample = Tuple[np.ndarray, np.ndarray, float]  # (state_vector, policy, value)

@dataclass
class CurriculumStage:
    name: str
    state_factory: Callable[[], GameState]
    iterations: int                         
    simulations: int = 100                  
    temperature: float = 1.0               
    temperature_cutoff: int = 999           


@dataclass
class TrainerConfig:
    buffer_size: int = 50_000
    batch_size: int = 256
    min_buffer_size: int = 1_000
    lr: float = 1e-3
    weight_decay: float = 1e-4
    train_steps_per_iter: int = 5
    puct: float = 1.5
    checkpoint_dir: str = "checkpoints"
    save_every: int = 10                   


# ─── Replay buffer ────────────────────────────────────────────────────────────

class ReplayBuffer:
    def __init__(self, maxlen: int):
        self.buffer: deque[Sample] = deque(maxlen=maxlen)

    def add(self, samples: List[Sample]) -> None:
        self.buffer.extend(samples)

    def sample(self, n: int) -> List[Sample]:
        return random.sample(self.buffer, min(n, len(self.buffer)))

    def __len__(self) -> int:
        return len(self.buffer)


# ─── Self-play ────────────────────────────────────────────────────────────────

def _get_policy_target(root, temperature: float) -> np.ndarray:
    counts = np.zeros(MOVE_VECTOR_LENGTH, dtype=np.float32)
    for move, child in root.children.items():
        counts[move] = child.visit_count

    if temperature == 0.0 or counts.sum() == 0:
        best = int(np.argmax(counts))
        policy = np.zeros(MOVE_VECTOR_LENGTH, dtype=np.float32)
        policy[best] = 1.0
        return policy

    counts **= 1.0 / temperature
    return counts / counts.sum()


def _resolve_luck(state: GameState) -> tuple[GameState, list[int]]:
    luck_trajectory = []
    while state.is_luck:
        outcomes = Updater.get_luck_outcomes(state)
        idx = random.randrange(len(outcomes))
        state = outcomes[idx]
        luck_trajectory.append(idx)
    return state, luck_trajectory


def self_play_game(
    mcts: MCTS,
    state_factory: Callable[[], GameState],
    temperature: float,
    temperature_cutoff: int,
) -> List[Tuple[np.ndarray, np.ndarray, np.float32]]:
    
    state = state_factory()
    state, _ = _resolve_luck(state)

    history: List[Tuple[np.ndarray, np.ndarray]] = []
    move_num = 0

    while True:
        winner = Updater.get_state_winner(state)
        if winner != 0:
            break

        temp = temperature if move_num < temperature_cutoff else 0.0

        root = mcts.search(state)
        policy = _get_policy_target(root, temp)

        history.append((state.vector.copy(), policy))

        move = int(np.random.choice(MOVE_VECTOR_LENGTH, p=policy))
        state = Updater.get_next_state(state, move)
        state, luck_history = _resolve_luck(state)
        mcts.update_root(move, luck_history)

        move_num += 1

    winner = Updater.get_state_winner(state)
    return [(sv, pt, np.float32(winner)) for sv, pt in history]


# ─── Training step ────────────────────────────────────────────────────────────

def _train_step(
    model: AlphaTiger,
    optimizer: optim.Optimizer,
    batch: List[Sample],
    device: torch.device
) -> Tuple[float, float, float]:
    states, policies, values = zip(*batch)

    state_t  = torch.tensor(np.array(states),   dtype=torch.float32, device=device)
    policy_t = torch.tensor(np.array(policies), dtype=torch.float32, device=device)
    value_t  = torch.tensor(np.array(values),   dtype=torch.float32, device=device).unsqueeze(1)

    pred_value, pred_logits = model(state_t)

    value_loss  = nn.MSELoss()(pred_value, value_t)
    log_probs   = torch.log_softmax(pred_logits, dim=-1)
    policy_loss = -(policy_t * log_probs).sum(dim=-1).mean()

    loss = value_loss + policy_loss

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item(), value_loss.item(), policy_loss.item()


# ─── Main training loop ───────────────────────────────────────────────────────

def train(
    curriculum: List[CurriculumStage],
    config: TrainerConfig = TrainerConfig(),
    resume_path: Optional[str] = None,
) -> AlphaTiger:
    
    os.makedirs(config.checkpoint_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model     = AlphaTiger().to(device)
    optimizer = optim.Adam(
        model.parameters(), lr=config.lr, weight_decay=config.weight_decay
    )
    buffer    = ReplayBuffer(config.buffer_size)

    global_iter = 0
    if resume_path and os.path.exists(resume_path):
        global_iter = load_checkpoint(model, optimizer, resume_path)
        print(f"Resumed ({model}) from iteration {global_iter}  ({resume_path}) on ({device})")

    for stage in curriculum:
        print(f"\n{'='*60}")
        print(f"  Stage: {stage.name}")
        print(f"  Iterations: {stage.iterations}  |  Simulations: {stage.simulations}")
        print(f"  Temperature: {stage.temperature}  (greedy after move {stage.temperature_cutoff})")
        print(f"{'='*60}")

        games_played = 0
        
        # Share memory for multiprocessing
        model.share_memory() 
        num_workers = 8
        
        # Safe context for PyTorch on Linux
        ctx = mp.get_context("spawn")

        while games_played < stage.iterations:
            batch_size = min(num_workers, stage.iterations - games_played)
            
            # ── Self-play (Batched) ──────────────────────────────────────────
            model.eval()
            
            # Note the mp_context=ctx argument being used here
            with ProcessPoolExecutor(max_workers=batch_size, mp_context=ctx) as executor:
                futures = []
                for _ in range(batch_size):
                    mcts_worker = MCTS(model, simulations=stage.simulations, puct=config.puct)
                    futures.append(
                        executor.submit(
                            self_play_game,
                            mcts_worker,
                            stage.state_factory,
                            stage.temperature,
                            stage.temperature_cutoff,
                        )
                    )
                
                batch_samples = [] 
                for future in futures:
                    samples = future.result()
                    buffer.add(samples)
                    batch_samples.extend(samples)
                    global_iter += 1
            
            games_played += batch_size

            # ── Training (Sequential) ────────────────────────────────────────
            total_loss = val_loss = pol_loss = 0.0
            steps = 0

            model.train()
            if len(buffer) >= config.min_buffer_size:
                total_train_steps = config.train_steps_per_iter * batch_size
                
                for _ in range(total_train_steps):
                    batch = buffer.sample(config.batch_size)
                    tl, vl, pl = _train_step(model, optimizer, batch, device)
                    total_loss += tl
                    val_loss   += vl
                    pol_loss   += pl
                    steps      += 1

            # ── Logging ──────────────────────────────────────────────────────
            prefix = f"[{stage.name}] iter {games_played:>4}/{stage.iterations} | buf {len(buffer):>6}"
            if steps:
                if len(batch_samples) == 0:
                    print("DEBUG: Batch ended with zero samples! Check your GameState initialization.")
                else:
                    print(
                        f"{prefix} | loss {total_loss/steps:.4f} "
                        f"(val {val_loss/steps:.4f}  pol {pol_loss/steps:.4f})"
                        f" | batch samples {len(batch_samples)} | winner {'british' if samples[0][2] == 1 else 'mysore'}"
                    )
            else:
                print(f"{prefix} | warming up ({len(buffer)}/{config.min_buffer_size})")

            # ── Checkpoint ───────────────────────────────────────────────────
            if global_iter % config.save_every == 0 or games_played == stage.iterations:
                path = os.path.join(config.checkpoint_dir, f"ckpt_{global_iter:06d}.pt")
                save_checkpoint(model, optimizer, global_iter, path)
                print(f"  ↳ saved {path}")

    final_path = os.path.join(config.checkpoint_dir, "final.pt")
    save_checkpoint(model, optimizer, global_iter, final_path)
    print(f"\nTraining complete — final model saved to {final_path}")
    return model

if __name__ == "__main__":
    # REQUIRED for PyTorch multiprocessing on Linux clusters
    mp.set_start_method("spawn", force=True)
    curriculum_train()