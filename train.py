#!/usr/bin/env python3
"""
Tigers Day AI — Training Entry Point

Usage:
  python train.py                           # default settings
  python train.py --iterations 200 --simulations 500 --lr 0.001 --resume
  python train.py --stage 3 --device cuda   # start from curriculum stage 3

All available flags are documented below.
"""

import argparse
import logging
import sys
import os
import torch

# ── make game/ importable ─────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "game"))

from ai.neural    import AlphaTiger
from ai.trainer  import Trainer
from ai.curriculum import NUM_STAGES


def parse_args():
    p = argparse.ArgumentParser(description="Train the Tigers Day AI via self-play.")

    # Training loop
    p.add_argument("--iterations",       type=int,   default=100,    help="Number of training iterations")
    p.add_argument("--games_per_iter",   type=int,   default=25,     help="Self-play games per iteration")
    p.add_argument("--simulations",      type=int,   default=200,    help="MCTS simulations per move")
    p.add_argument("--batch_size",       type=int,   default=256,    help="Mini-batch size for gradient steps")
    p.add_argument("--samples_per_step", type=int,   default=512,    help="Samples drawn from buffer per step")
    p.add_argument("--buffer_capacity",  type=int,   default=50_000, help="Replay buffer capacity")

    # Optimiser
    p.add_argument("--lr",     type=float, default=1e-3,  help="Initial learning rate")
    p.add_argument("--c_reg",  type=float, default=1e-4,  help="L2 regularisation coefficient")

    # Curriculum
    p.add_argument("--stage",            type=int,   default=0,
                   help=f"Starting curriculum stage (0-{NUM_STAGES-1})")
    p.add_argument("--stage_threshold",  type=float, default=0.20,
                   help="Loss threshold to advance curriculum stage")

    # Infrastructure
    p.add_argument("--device",          type=str,  default="auto",
                   help="Device: 'cpu', 'cuda', 'mps', or 'auto'")
    p.add_argument("--checkpoint_dir",  type=str,  default="ai/checkpoints")
    p.add_argument("--resume",          action="store_true",
                   help="Resume from best_model.pth if available")

    # Logging
    p.add_argument("--log_level", type=str, default="INFO",
                   help="Logging level: DEBUG, INFO, WARNING, ERROR")

    return p.parse_args()


def resolve_device(requested: str) -> str:
    if requested == "auto":
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    return requested


def main():
    args   = parse_args()
    device = resolve_device(args.device)

    # ── logging ───────────────────────────────────────────────────────────────
    logging.basicConfig(
        level  = getattr(logging, args.log_level.upper(), logging.INFO),
        format = "%(asctime)s %(levelname)-7s %(name)s — %(message)s",
        datefmt= "%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("training.log", mode="a"),
        ],
    )
    logger = logging.getLogger("train")
    logger.info("Tigers Day AI — training starting")
    logger.info("Device: %s | Iterations: %d | Simulations: %d",
                device, args.iterations, args.simulations)
    logger.info("Curriculum start stage: %d / %d", args.stage, NUM_STAGES - 1)

    # ── model ─────────────────────────────────────────────────────────────────
    model = AlphaTiger()
    logger.info("Model parameters: {:,}".format(
        sum(p.numel() for p in model.parameters())
    ))

    # ── trainer ───────────────────────────────────────────────────────────────
    trainer = Trainer(
        model                = model,
        iterations           = args.iterations,
        games_per_iter       = args.games_per_iter,
        simulations          = args.simulations,
        batch_size           = args.batch_size,
        samples_per_step     = args.samples_per_step,
        lr                   = args.lr,
        checkpoint_dir       = args.checkpoint_dir,
        device               = device,
        stage_loss_threshold = args.stage_threshold,
        buffer_capacity      = args.buffer_capacity,
        resume               = args.resume,
        start_stage          = args.stage,
    )

    trainer.run()


if __name__ == "__main__":
    main()